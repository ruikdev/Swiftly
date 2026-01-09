# 🚀 Swiftly

<div align="center">

**The Open Source Netlify Alternative**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black.svg)](https://flask.palletsprojects.com/)

*Deploy your static sites instantly with a simple API and CLI*

Originally built for [Flavortown Hack Club](https://flavortown.hackclub.com/) 🍔

[Features](#features) • [Quick Start](#quick-start) • [API Documentation](#api-documentation) • [CLI Usage](#cli-usage)

**[🇫🇷 Version Française](README.fr.md)**

</div>

---

## 📖 About

**Swiftly** is a lightweight, open-source platform for deploying and hosting static HTML sites. Built with Flask, it provides a simple REST API and CLI tool to manage your deployments.

This project was originally created for the [Flavortown Hack Club](https://flavortown.hackclub.com/) community to provide an easy way to deploy and share static sites.

Perfect for:
- 🎨 Personal portfolios
- 📝 Static blogs
- 🌐 Landing pages
- 🧪 Prototype demos
- 🏫 Student projects

## ✨ Features

- **🚀 Simple API** - Upload and deploy HTML files via REST API
- **💻 CLI Tool** - Command-line interface for easy deployment
- **📦 File Upload** - Direct HTML file upload support
- **🗂️ Site Management** - List, add, and delete sites easily
- **🔒 Secure** - File name sanitization and validation
- **📊 JSON Database** - Simple file-based storage
- **🆓 100% Open Source** - MIT License

## 🏁 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ruikdev/Swiftly.git
cd Swiftly
```

2. **Create a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the server**
```bash
python app.py
```

The server will start on `http://localhost:5000` 🎉

## 🔌 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### **GET** `/health`
Check if the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

---

#### **GET** `/api/sites`
List all deployed sites.

**Response:**
```json
{
  "sites": {
    "my-site": "my-site.html",
    "blog": "blog.html"
  }
}
```

---

#### **POST** `/api/sites`
Upload and deploy a new site.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `name` (string, required): The site name/identifier
- `file` (file, required): HTML file to upload

**Example with curl:**
```bash
curl -X POST http://localhost:5000/api/sites \
  -F "name=my-awesome-site" \
  -F "file=@index.html"
```

**Success Response (201):**
```json
{
  "message": "Site 'my-awesome-site' ajouté avec succès",
  "site": {
    "my-awesome-site": "my-awesome-site.html"
  },
  "url": "/sites/my-awesome-site"
}
```

**Error Responses:**
- `400` - Missing required fields or invalid file
- `404` - No file in request
- `409` - Site name already exists

---

#### **DELETE** `/api/sites/<site_name>`
Delete a deployed site.

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/sites/my-site
```

**Success Response (200):**
```json
{
  "message": "Site 'my-site' supprimé avec succès"
}
```

---

#### **GET** `/sites/<site_name>`
Access a deployed site.

**Example:**
```
http://localhost:5000/sites/my-awesome-site
```

## 💻 CLI Usage

Swiftly comes with a powerful CLI tool for testing and managing your deployments.

### Setup
```bash
pip install requests
```

### Commands

**Check API health:**
```bash
python cli_api_test.py health
```

**List all sites:**
```bash
python cli_api_test.py list
```

**Deploy a new site:**
```bash
python cli_api_test.py add my-blog index.html
```

**Delete a site:**
```bash
python cli_api_test.py delete my-blog
```

**Show help:**
```bash
python cli_api_test.py help
```

## 📁 Project Structure

```
Swiftly/
├── app.py                 # Main Flask application
├── cli_api_test.py        # CLI tool for testing
├── requirements.txt       # Python dependencies
├── db/
│   └── sites.json        # Site database
├── sites/                # Deployed HTML files
├── templates/
│   └── base.html         # Landing page
└── README.md
```

## 🛠️ Configuration

The application uses the following defaults:

- **Host:** `0.0.0.0`
- **Port:** `5000`
- **Database:** `db/sites.json`
- **Sites folder:** `sites/`

You can modify these in [app.py](app.py).

## 🔐 Security Features

- ✅ Filename sanitization with `secure_filename()`
- ✅ HTML file validation
- ✅ Duplicate name prevention
- ✅ Path traversal protection

## 🗺️ Roadmap

### Coming Soon
- [ ] Custom domain support
- [ ] SSL/TLS certificates automation
- [ ] Multi-file site deployment (entire directories)
- [ ] Git integration for automatic deployments
- [ ] Dashboard UI for site management
- [ ] Environment variables support
- [ ] Site analytics
- [ ] CDN integration
- [ ] Webhook support for CI/CD
- [ ] User authentication system
- [ ] Enhanced security features

### In Progress
- [x] Basic HTML file deployment
- [x] REST API
- [x] CLI tool
- [x] File upload via API

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Inspired by [Netlify](https://www.netlify.com/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- Created for [Flavortown Hack Club](https://flavortown.hackclub.com/) community

---

<div align="center">

Made with ❤️ by [ruikdev](https://github.com/ruikdev)

⭐ Star this repo if you find it useful!

</div>



