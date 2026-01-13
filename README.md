# 🚀 Swiftly

<div align="center">

**The Open Source Netlify Alternative**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black.svg)](https://flask.palletsprojects.com/)

*Deploy your static sites instantly with a simple API and CLI*

Originally built for [Flavortown Hack Club](https://flavortown.hackclub.com/) 🍔

[Features](#features) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [CLI Usage](#-cli-usage)

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
 - **📦 File & Directory Upload** - Direct HTML file upload and full directory upload (preserves structure)
 - **📊 Dashboard UI** - Web interface for managing sites (login, deploy, delete)
- **🗂️ Site Management** - List, add, and delete sites easily
- **🔒 Secure** - File name sanitization and validation
- **📊 JSON Database** - Simple file-based storage
- **🆓 100% Open Source** - MIT License

## 🏁 Quick Start

### Prerequisites

- Python 3.8+

### 🚀 Easiest Way (Recommended)

#### On Linux/macOS
```bash
./swiftly.sh
```

#### On Windows
Double-click `swiftly.bat` or run in Command Prompt:
```cmd
swiftly.bat
```

That's it! The scripts will automatically:
- ✅ Check Python installation
- 📦 Install `requests` if needed
- 🚀 Launch the CLI

### Manual Installation (For Server Setup)

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

## 🖥️ Dashboard Web

Swiftly now includes a web dashboard to manage your sites without the CLI.

- **URL**: `http://localhost:5000/dashboard`
- **Features**:
  - Login / Register from the browser
  - List your sites (preview, file count)
  - Deploy via a form (upload full folder or individual files)
  - Delete sites

The dashboard uses Tailwind and matches the landing page style. To use it, start the server (`python app.py`) and open the URL above. The deploy form supports drag & drop of folders and validates the presence of an `index.html`.

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

## 🌐 Wildcard Subdomains

Swiftly now supports wildcard subdomains! This means you can deploy your sites to subdomains like `example.swiftly.ruikdev.me` effortlessly. Simply configure your DNS settings and let Swiftly handle the rest.

### Key Benefits:
- Automatic SSL certificates for wildcard subdomains.
- Seamless routing for static files and resources.
- Easy setup with Cloudflare DNS.

Refer to the [documentation](#📄-api-documentation) for detailed instructions.

## 💻 CLI Usage

Swiftly comes with a powerful interactive CLI tool for managing your deployments. The CLI can be used independently from the server!

### Quick Installation (CLI Only)

If you only want to use the CLI (without running the server):

1. **Download the CLI file:**
```bash
curl -O https://raw.githubusercontent.com/ruikdev/Swiftly/main/swiftly_cli.py
```

Or copy `swiftly_cli.py` from the repository.

2. **Install the only required dependency:**
```bash
pip install requests
```

3. **Run the CLI:**
```bash
python3 swiftly_cli.py
```

### Full Installation (With Server)

If you want to run both the server and CLI:

```bash
git clone https://github.com/ruikdev/Swiftly.git
cd Swiftly
pip install -r requirements.txt
```

### Running the CLI

Start the interactive CLI:

```bash
python3 swiftly_cli.py
```

On the first run, you'll be asked to select your language:
- 🇫🇷 Français (French)
- 🇬🇧 English

### Features

The CLI offers an interactive menu with the following options:

**Account Management:**
- Create a new account (email + password)
- Login
- View your profile
- Change your email
- Change your password
- Logout

**Site Management:**
- List all your deployed sites
- Deploy a new site (upload HTML file)
- Delete a site

**Other:**
- Check API health
- Change language anytime (option 9)

### Example Workflow

```
1. Start CLI: python3 swiftly_cli.py
2. Select language (French or English)
3. Create account or login
4. Deploy your HTML files
5. List your sites
6. Share your site URLs!
```

### Credentials Storage

Your credentials are securely stored locally in `~/.swiftly_config.json` with restricted permissions (600). You won't need to login again on the same machine.

### Authentication Headers

All API requests made by the CLI automatically include your credentials in these headers:
- `X-User-Email`: Your email
- `X-User-Password`: Your password

---

## 💻 CLI Usage

Swiftly comes with a powerful CLI tool for testing and managing your deployments.

## 📁 Project Structure

```
Swiftly/
├── app.py                      # Main Flask application
├── swiftly_cli.py              # Interactive CLI script
├── swiftly.sh                  # Installer / launcher (Linux/macOS)
├── swiftly.bat                 # Installer / launcher (Windows)
├── requirements.txt            # Python dependencies
├── db/
│   ├── sites.json              # Site database (local)
│   └── users.json              # Users database (local)
├── sites/                      # Deployed site folders
├── templates/                  # Jinja2 templates
│   ├── base.html
│   ├── dashboard_layout.html
│   ├── auth_login.html
│   ├── auth_register.html
│   ├── dashboard_home.html
│   ├── dashboard_deploy.html
│   └── dashboard_profile.html
├── swiftly/                    # Main package
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── site.py
│   │   └── user.py
│   ├── routes/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── sites.py
│   │   ├── user.py
│   │   └── dashboard.py
│   └── utils/
│       └── decorators.py
└── README.fr.md
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
- [x] Dashboard UI for site management
- [ ] Environment variables support
- [ ] Site analytics
- [ ] CDN integration
- [ ] Webhook support for CI/CD

### In Progress
- [x] Basic HTML file deployment
- [x] REST API
- [x] CLI tool
- [x] File upload via API
- [x] User authentication system
- [x] Enhanced security features
- [ ] Dashboard UI for site management
 - [x] Dashboard UI for site management

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



