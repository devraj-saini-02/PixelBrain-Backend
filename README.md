# 🧠 PixelBrain – AI Powered Image Intelligence Backend

PixelBrain is a FastAPI-based backend that performs **AI-driven image understanding, enhancement, and storage**.  
It combines **computer vision, deep learning, and cloud image delivery** into one unified platform.

This backend powers PixelBrain’s ability to:
- Understand scenes (indoor / outdoor / day / night / weather)
- Detect objects and faces
- Apply intelligent image filters
- Store and transform images via Cloudinary
- Provide secure access with JWT authentication

---

## 🚀 Features

### 🔐 Authentication
- OAuth2 Password Flow
- JWT Bearer tokens
- Secure password hashing
- Protected API routes

### 🖼 AI Image Processing
- Upload images via API
- Automatic:
  - Indoor / Outdoor detection
  - Day / Night classification
  - Weather detection (for outdoor images)
  - Primary object detection (largest bounding box)
- Smart AI filters (brightness, contrast, dehaze, etc.)
- Optional text-based enhancement prompts

### ☁️ Cloudinary Integration
- Stores all processed images
- Saves:
  - `secure_url`
  - `public_id`
- Supports:
  - Resize
  - Crop
  - Aspect-ratio control
  - Format optimization

### 🔍 Image Search & Analytics
Search stored images by:
- Indoor / Outdoor
- Weather
- Daytime
- Detected objects
- Applied filters

### 🧠 Machine Learning
- TensorFlow-based scene & attribute models
- COCO-based object detection
- Face detection & emotion pipeline
- OpenCV image processing

---

## 🏗 Tech Stack

| Layer | Technology |
|------|------------|
| API | FastAPI |
| Auth | OAuth2 + JWT |
| Database | SQLite / PostgreSQL |
| ORM | SQLAlchemy |
| AI | TensorFlow, OpenCV |
| Object Detection | COCO / YOLO |
| Image Storage | Cloudinary |
| Containerization | Docker |

---

## 📁 Project Structure

```
pixelbrain-backend/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── oauth2.py
│   ├── utils.py
│   │
│   ├── ml/
│   │   ├── scene_model.py
│   │   ├── object_detector.py
│   │   └── filters.py
│   │
│   └── routers/
│       ├── auth.py
│       ├── user.py
│       ├── image.py
│       └── search.py
│
├── requirements.txt
├── Dockerfile
├── .env
└── README.md
```

---

## 🔑 Environment Variables (`.env`)

```
DATABASE_URL=sqlite:///./pixelbrain.db

SECRET_KEY=your_jwt_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

CLOUDINARY_CLOUD_NAME=xxxxx
CLOUDINARY_API_KEY=xxxxx
CLOUDINARY_API_SECRET=xxxxx
```

---

## ⚙️ Installation

```
git clone https://github.com/yourusername/pixelbrain-backend.git
cd pixelbrain-backend

python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate  # Linux / Mac

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## 📡 API Docs

```
http://127.0.0.1:8000/docs
```

---

## 🖼 Image Upload Flow

1. Client uploads image  
2. Server runs ML models  
3. Filters applied  
4. Uploaded to Cloudinary  
5. Metadata stored in DB  
6. Final JSON returned  

---

## 📦 Sample API Response

```json
{
  "image_url": "https://res.cloudinary.com/.../image.png",
  "public_id": "images/qlqj58e0dhvdipiuxitu",
  "indoor": false,
  "daytime": "day",
  "weather": "clear",
  "primary_object": "car",
  "filters": ["brightness", "contrast"]
}
```

---

## 🐳 Docker

```
docker build -t pixelbrain .
docker run -p 8000:8000 pixelbrain
```

---

## 🔐 Security

- Passwords hashed using bcrypt  
- JWT tokens for API authentication  
- Protected endpoints  
- Secrets stored in `.env`  

---

## 📈 Roadmap

- Face recognition & emotion detection  
- NSFW filtering  
- Super-resolution & deblur  
- Video support  
- Mobile app integration  

---

## 👨‍💻 Author

Devraj Saini  
Creator of PixelBrain 🚀

