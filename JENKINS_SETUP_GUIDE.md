# 🚀 Jenkins Setup Guide for Beginners
# Health AI Assistant - Local Jenkins CI/CD

## 📚 What We're Going to Do:
1. Install Jenkins on your computer
2. Set it up to watch your code
3. Make it automatically build Docker containers
4. Create a pipeline that runs when you change code

## 🔧 Step 1: Install Jenkins

### Windows Installation:

#### Method 1: Using Docker (Easiest)
```batch
# Since you already have Docker, this is the simplest way!

# 1. Create a Jenkins data directory
mkdir C:\jenkins_data

# 2. Run Jenkins in Docker
docker run -d ^
  --name jenkins ^
  -p 8080:8080 ^
  -p 50000:50000 ^
  -v C:\jenkins_data:/var/jenkins_home ^
  -v /var/run/docker.sock:/var/run/docker.sock ^
  jenkins/jenkins:lts

# 3. Get the initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

#### Method 2: Direct Installation
```batch
# 1. Download Jenkins from: https://www.jenkins.io/download/
# 2. Download the Windows installer (.msi file)
# 3. Run the installer as Administrator
# 4. Follow the setup wizard
```

### What This Does:
- **Port 8080**: Web interface (where you'll access Jenkins)
- **Port 50000**: For connecting additional Jenkins agents
- **Volume mapping**: Keeps your Jenkins data safe
- **Docker socket**: Allows Jenkins to build Docker images

## 🌐 Step 2: Access Jenkins

1. Open your browser
2. Go to: http://localhost:8080
3. You'll see a "Getting Started" page asking for a password

### Getting the Admin Password:
```batch
# If using Docker method:
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# If direct installation:
# Check: C:\Program Files\Jenkins\secrets\initialAdminPassword
```

## 🔐 Step 3: Initial Setup

### When you first access Jenkins:

1. **Enter Admin Password**: Paste the password you got above
2. **Install Plugins**: Choose "Install suggested plugins" (this takes 5-10 minutes)
3. **Create Admin User**: 
   - Username: `admin` (or your choice)
   - Password: `your_secure_password`
   - Full Name: `Your Name`
   - Email: `your_email@example.com`
4. **Jenkins URL**: Keep as `http://localhost:8080/`
5. **Start Using Jenkins**: Click "Start using Jenkins"

## 🎯 What You'll See:
- **Dashboard**: Main page showing all your projects
- **New Item**: Create new projects/pipelines
- **Manage Jenkins**: Settings and configuration
- **Build History**: See what happened with each build

## 📊 Jenkins Terms for Beginners:

- **Job/Project**: A task Jenkins performs (like building your app)
- **Build**: One execution of a job
- **Pipeline**: A series of steps (build → test → deploy)
- **Workspace**: Folder where Jenkins works with your code
- **Agent/Node**: Computer that runs the jobs
- **Plugin**: Add-on that gives Jenkins new features

## 🔧 Step 4: Install Required Plugins

Go to "Manage Jenkins" → "Manage Plugins" → "Available" and install:

1. **Docker Pipeline** - To work with Docker
2. **Git Plugin** - To get code from Git
3. **Pipeline** - For advanced automation
4. **Blue Ocean** - Modern, easy-to-use interface
5. **Workspace Cleanup** - Keeps things tidy

### How to Install:
1. Search for each plugin name
2. Check the box next to it
3. Click "Install without restart"
4. Wait for installation to complete

## 🎮 Next Steps:
Once Jenkins is installed and running, we'll:
1. Create your first pipeline
2. Connect it to your Health AI Assistant project
3. Make it automatically build and test your Docker containers
4. Set up notifications when builds succeed or fail

## 🆘 Troubleshooting:

**Can't access http://localhost:8080?**
- Wait 2-3 minutes for Jenkins to fully start
- Check if Docker container is running: `docker ps`
- Restart Jenkins: `docker restart jenkins`

**Forgot admin password?**
- Get it again: `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword`

**Plugins won't install?**
- Check internet connection
- Try again later (Jenkins servers might be busy)

Ready to install Jenkins? Let me know when you're ready for the next step!
