# Backend Integration Guide

## "Accept and Finalize" Feature - Backend Requirements

### How It Works in Frontend

When a user clicks "Accept & Finalize" button on the ReviewPage (`/review/:id`), the frontend executes this logic:

```javascript
async function acceptAndFinalize() {
  // Step 1: Try dedicated finalize endpoint (PREFERRED)
  try {
    await POST /api/documents/{id}/finalize/
  } catch (error) {
    // Step 2: Fallback to PATCH with status field (REQUIRED MINIMUM)
    await PATCH /api/documents/{id}/
    Body: { "status": "approved" }
  }
}
```

### Backend Implementation Options

You have **TWO OPTIONS** to support this feature:

---

## Option 1: Minimal Implementation (PATCH only)

**What you need**: A Django ViewSet that supports `partial_update` with a `status` field.

### Requirements:

1. **Document Model** must have a `status` field:
```python
# models.py
class Document(models.Model):
    # ... other fields ...
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('processed', 'Processed'),
            ('approved', 'Approved'),  # ← This is what frontend sets
            ('error', 'Error'),
        ],
        default='pending'
    )
```

2. **ViewSet** must support PATCH:
```python
# views.py
from rest_framework import viewsets

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    # partial_update is automatically supported by ModelViewSet
```

3. **Serializer** must include `status` field:
```python
# serializers.py
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'status', 'original_filename', ...]  # Include status
```

4. **URL routing**:
```python
# urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

### Testing:
```bash
# This should work:
curl -X PATCH http://localhost:8000/api/documents/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'

# Expected response:
{
  "id": 1,
  "status": "approved",
  "original_filename": "document.pdf",
  ...
}
```

---

## Option 2: Dedicated Finalize Endpoint (RECOMMENDED)

**What you need**: A custom action on the ViewSet for better control and business logic.

### Implementation:

```python
# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """
        Custom endpoint to finalize a document.
        Handles business logic like validation, notifications, etc.
        """
        document = self.get_object()
        
        # Add your business logic here:
        # - Validate extracted fields are complete
        # - Send notifications
        # - Update related records
        # - Log the action
        
        # Update status
        document.status = 'approved'
        document.save()
        
        # Optionally update other fields
        # document.finalized_by = request.user
        # document.finalized_at = timezone.now()
        # document.save()
        
        serializer = self.get_serializer(document)
        return Response(serializer.data)
```

### URL Pattern:
This automatically creates: `POST /api/documents/{id}/finalize/`

### Testing:
```bash
# This will work:
curl -X POST http://localhost:8000/api/documents/1/finalize/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected response:
{
  "id": 1,
  "status": "approved",
  "original_filename": "document.pdf",
  ...
}
```

---

## Why Option 2 is Better

### Advantages of Dedicated Endpoint:

1. **Business Logic Separation**:
   - Can validate that all required fields are filled
   - Can check user permissions specifically for finalization
   - Can prevent re-finalization of already approved documents

2. **Audit Trail**:
   ```python
   document.finalized_by = request.user
   document.finalized_at = timezone.now()
   ```

3. **Side Effects**:
   - Send email notifications
   - Trigger downstream processes
   - Update analytics/metrics
   - Generate reports

4. **Validation**:
   ```python
   if not document.extracted_fields:
       return Response(
           {"error": "Cannot finalize document without extracted fields"},
           status=status.HTTP_400_BAD_REQUEST
       )
   ```

5. **Clear Intent**: 
   - `POST /finalize/` is more semantic than `PATCH` with status change
   - Easier to understand API usage
   - Better API documentation

---

## Frontend Behavior Summary

### Current Implementation:

```
User clicks "Accept & Finalize"
    ↓
Try: POST /api/documents/:id/finalize/
    ↓
If 404 or error:
    ↓
Fallback: PATCH /api/documents/:id/ with {"status": "approved"}
    ↓
If success:
    ↓
Show success message
    ↓
Wait 2 seconds
    ↓
Redirect to /bulk-review
```

### What This Means:

1. **If you implement Option 2** (dedicated endpoint):
   - Frontend will use `POST /finalize/` ✅
   - Cleaner, more semantic
   - Better for business logic

2. **If you only implement Option 1** (PATCH):
   - Frontend will fallback to `PATCH` ✅
   - Still works perfectly
   - Simpler backend

3. **If you implement BOTH**:
   - Frontend prefers `POST /finalize/` ✅
   - Falls back to PATCH if finalize fails
   - Maximum compatibility

---

## Recommended Implementation Steps

### Step 1: Verify Your Current Setup

Check if you already have the minimum requirements:

```python
# Check your models.py
class Document(models.Model):
    status = models.CharField(...)  # ← Does this exist?

# Check your serializers.py
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [..., 'status', ...]  # ← Is 'status' included?

# Check your views.py
class DocumentViewSet(viewsets.ModelViewSet):  # ← Using ModelViewSet?
    # partial_update is automatic
```

### Step 2: Test PATCH Endpoint

```bash
# Test if PATCH already works:
curl -X PATCH http://localhost:8000/api/documents/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'
```

**If this works**: ✅ You're done! Frontend will work.

**If this fails**: Add the missing pieces from Option 1.

### Step 3: (Optional) Add Finalize Endpoint

Only if you want better control and business logic:

```python
# Add to your DocumentViewSet
@action(detail=True, methods=['post'])
def finalize(self, request, pk=None):
    document = self.get_object()
    document.status = 'approved'
    document.save()
    serializer = self.get_serializer(document)
    return Response(serializer.data)
```

---

## Common Issues and Solutions

### Issue 1: "Method PATCH not allowed"

**Cause**: ViewSet doesn't support partial updates.

**Solution**: 
```python
# Use ModelViewSet (not ReadOnlyModelViewSet)
class DocumentViewSet(viewsets.ModelViewSet):  # ✅
    # not: viewsets.ReadOnlyModelViewSet  # ❌
```

### Issue 2: "Field 'status' is read-only"

**Cause**: Serializer has `status` as read-only.

**Solution**:
```python
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'status', ...]
        # Don't include 'status' in read_only_fields
```

### Issue 3: "404 Not Found" on finalize endpoint

**Cause**: Custom action not registered.

**Solution**:
```python
# Make sure you're using DefaultRouter (not SimpleRouter)
from rest_framework.routers import DefaultRouter  # ✅

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
```

---

## Testing Checklist

### Backend Tests:

- [ ] PATCH `/api/documents/1/` with `{"status": "approved"}` returns 200
- [ ] Response includes updated status field
- [ ] (Optional) POST `/api/documents/1/finalize/` returns 200
- [ ] Authentication is required (401 without token)
- [ ] Invalid status values are rejected (400)

### Frontend Tests:

- [ ] Click "Accept & Finalize" on review page
- [ ] Success message appears
- [ ] Redirects to document list after 2 seconds
- [ ] Document status updates in the list
- [ ] Works even if finalize endpoint doesn't exist (uses PATCH fallback)

---

## Summary

### Minimum Required (Option 1):
```
✅ Document model has 'status' field
✅ DocumentSerializer includes 'status' in fields
✅ DocumentViewSet is ModelViewSet (supports PATCH)
✅ URL routing includes the viewset
```

### Recommended (Option 2):
```
✅ Everything from Option 1
✅ Custom @action for finalize endpoint
✅ Business logic in finalize method
✅ Proper error handling and validation
```

### Frontend Compatibility:
```
✅ Works with Option 1 only (PATCH fallback)
✅ Works with Option 2 only (dedicated endpoint)
✅ Works with both (prefers dedicated, falls back to PATCH)
✅ Graceful error handling if neither works
```

The frontend is designed to be **maximally compatible** with whatever backend implementation you choose!