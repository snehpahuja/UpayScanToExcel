UPAY Frontend (Prototype loader)
================================

Files from your prototype were copied into `public/protos/` so the React app can load them directly and match the prototype exactly.

To run locally (on your machine) do the following in a terminal in this project folder:

1. Install dependencies (requires npm or yarn):
   npm install
2. Start dev server:
   npm run dev
   (opens at http://localhost:3000)

What this scaffolding does:
- Serves your original HTML prototypes unchanged from /public/protos so visual match is exact.
- Provides routing pages for each prototype HTML file.
- Uses React + Tailwind so we can incrementally convert prototype pages into proper React components and wire API calls to your Django backend.

Next steps I can do (one at a time):
- Convert a specific prototype page into React components and wire its form/buttons to the Django API.
- Add authentication flow (login page + JWT integration).
- Replace prototype HTML with Tailwind-based components for responsive layout.

Download the project folder below after you run npm install locally.
