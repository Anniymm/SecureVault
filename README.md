# 📁 SecureVault – Encrypted File Storage & Sharing System
### Use branches 

SecureVault is a Django-based application that offers secure file storage with encryption, user-specific activity logging, and robust access controls. Designed with security and user privacy in mind, it ensures that users can upload, manage, and download their files safely.

---

## 🚀 Features

- **Encrypted File Storage**: Files are encrypted using Fernet symmetric encryption before storage.
- **User Authentication**: Secure access using JWT authentication. Enables 2FA authentication.
- **File Management**:
  - Upload, download, and delete files.
  - Pagination and filtering by file extension.
  - Download count tracking.
- **Activity Logging**: Logs every user action (upload, download, delete) with timestamps.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Anniymm/SecureVault.git
cd SecureVault
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and add the following:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
# Fernet Encryption Key
FERNET_MASTER_KEY=your_fernet_key

```

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

---

## 📦 API Endpoints

### Authentication

- **Obtain Token**: `POST /auth/token/`
- **Refresh Token**: `POST /auth/token/refresh/`

### File Operations

- **Upload File**: `POST /vault/upload/`
- **List Files**: `GET /vault/files/`
  - Supports pagination and filtering by extension.
- **Download File**: `GET /vault/download/<file_id>/`
- **Delete File**: `DELETE /vault/delete/<file_id>/`

### Activity Logs
### ! in progress
- **User Logs**: `GET /vault/logs/`

---

## 🔐 Security Considerations

- **Encryption**: All files are encrypted using Fernet before storage.
- **Authentication**: JWT is used for secure user authentication.
- **Permissions**: Users can only access their own files and logs. Files can be shared according to permissions.
- **Logging**: All file-related actions are logged per user for auditing.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙌 Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Fernet Encryption](https://cryptography.io/en/latest/fernet/)
- [django-storages](https://django-storages.readthedocs.io/en/latest/)
