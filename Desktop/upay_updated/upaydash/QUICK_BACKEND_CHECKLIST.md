# Quick Backend Checklist for Frontend Integration

## ✅ Minimum Requirements (Must Have)

### 1. Document Model
```python
class Document(models.Model):
    status = models.CharField(max_length=20, default='pending')
    # Must support values: 'pending', 'processing', 'processed', 'approved', 'error'
```

### 2. Document Serializer
```python
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'status', ...]  # Include 'status'
        # DON'T put 'status' in read_only_fields
```

### 3. Document ViewSet
```python
class DocumentViewSet(viewsets.ModelViewSet):  # Use ModelViewSet
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
```

### 4. URL Configuration
```python
router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
urlpatterns = [path('api/', include(router.urls))]
```

**Test**: `PATCH /api/documents/1/` with `{"status": "approved"}` should work.

---

## 🎯 Optional But Recommended

### Custom Finalize Endpoint
```python
class DocumentViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        document = self.get_object()
        document.status = 'approved'
        document.save()
        return Response(self.get_serializer(document).data)
```

**Test**: `POST /api/documents/1/finalize/` should work.

---

## 📊 Stats Endpoints (Optional)

### For Dashboard and HomePage

```python
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def stats_view(request):
    return Response({
        'total_documents': Document.objects.count(),
        'processed_count': Document.objects.filter(status='processed').count(),
        'pending_count': Document.objects.filter(status='pending').count(),
        'error_count': Document.objects.filter(status='error').count(),
    })

# urls.py
urlpatterns = [
    path('api/stats/', stats_view),
    # OR
    path('api/dashboard/stats/', stats_view),
]
```

---

## 👤 Profile Endpoint (Optional)

```python
# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    })

# urls.py
urlpatterns = [
    path('api/profile/', profile_view),
]
```

---

## 🔍 Quick Test Commands

### Test Authentication
```bash
# Get token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### Test Document PATCH (Minimum Required)
```bash
curl -X PATCH http://localhost:8000/api/documents/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'
```

### Test Finalize Endpoint (Optional)
```bash
curl -X POST http://localhost:8000/api/documents/1/finalize/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Stats Endpoint (Optional)
```bash
curl -X GET http://localhost:8000/api/stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Profile Endpoint (Optional)
```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🚦 Priority Levels

### 🔴 CRITICAL (Frontend won't work without these)
- ✅ JWT Authentication (`/api/token/`, `/api/token/refresh/`)
- ✅ Document List (`GET /api/documents/`)
- ✅ Document Detail (`GET /api/documents/:id/`)
- ✅ Document Upload (`POST /api/upload/files/`)
- ✅ Document Update (`PATCH /api/documents/:id/` with status field)

### 🟡 HIGH (Features will show placeholders)
- ⚠️ Stats endpoint for dashboard
- ⚠️ Finalize endpoint for better UX

### 🟢 LOW (Nice to have)
- ⚠️ Profile endpoint
- ⚠️ Additional stats breakdowns

---

## 💡 Frontend Behavior

| Backend State | Frontend Behavior |
|---------------|-------------------|
| Only PATCH works | ✅ Uses PATCH fallback, works perfectly |
| Only finalize works | ✅ Uses finalize endpoint, works perfectly |
| Both work | ✅ Prefers finalize, falls back to PATCH |
| Neither works | ❌ Shows error message to user |
| No stats endpoint | ✅ Shows "—" placeholder |
| No profile endpoint | ✅ Shows basic info from localStorage |

---

## 🎯 What to Implement First

1. **Day 1**: Verify PATCH endpoint works with status field
2. **Day 2**: Add stats endpoint for dashboard
3. **Day 3**: Add custom finalize endpoint (optional but nice)
4. **Day 4**: Add profile endpoint (optional)

The frontend is designed to work gracefully with whatever you implement!