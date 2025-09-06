@echo off
REM Jenkins Installation Script for Beginners
REM Health AI Assistant Project

echo 🚀 Jenkins Installation for Health AI Assistant
echo =============================================
echo.
echo This script will install Jenkins locally using Docker
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    echo    Then run this script again.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Create Jenkins data directory
echo 📁 Creating Jenkins data directory...
if not exist "C:\jenkins_data" (
    mkdir C:\jenkins_data
    echo ✅ Created C:\jenkins_data
) else (
    echo ✅ Jenkins data directory already exists
)

REM Stop existing Jenkins container if it exists
echo 🛑 Stopping any existing Jenkins container...
docker stop jenkins 2>nul
docker rm jenkins 2>nul

echo 🔄 Starting Jenkins container...
echo    This may take a few minutes to download Jenkins...

REM Run Jenkins container
docker run -d ^
  --name jenkins ^
  -p 8080:8080 ^
  -p 50000:50000 ^
  -v C:\jenkins_data:/var/jenkins_home ^
  -v /var/run/docker.sock:/var/run/docker.sock ^
  -v "%cd%":/workspace ^
  --restart unless-stopped ^
  jenkins/jenkins:lts

if errorlevel 1 (
    echo ❌ Failed to start Jenkins container
    pause
    exit /b 1
)

echo ✅ Jenkins container started successfully!
echo.
echo ⏳ Waiting for Jenkins to initialize (this takes 2-3 minutes)...
echo    You'll see "Jenkins is fully up and running" when ready.

REM Wait for Jenkins to start
timeout /t 30 /nobreak >nul

echo 🔍 Checking Jenkins status...
for /l %%x in (1, 1, 10) do (
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:8080 >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Jenkins is responding!
        goto :jenkins_ready
    )
    echo    Still starting... (attempt %%x/10)
)

:jenkins_ready
echo.
echo 🎉 Jenkins Installation Complete!
echo.
echo 📋 Next Steps:
echo ============
echo.
echo 1. Open your browser and go to: http://localhost:8080
echo.
echo 2. Get your admin password by running this command:
echo    docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
echo.
echo 3. Copy the password and paste it in Jenkins web interface
echo.
echo 4. Choose "Install suggested plugins"
echo.
echo 5. Create your admin user account
echo.
echo 📊 Jenkins Management Commands:
echo ===============================
echo.
echo View logs:     docker logs jenkins
echo Stop Jenkins:  docker stop jenkins
echo Start Jenkins: docker start jenkins
echo Restart:       docker restart jenkins
echo.
echo 🔑 Get admin password now:

REM Get the admin password
timeout /t 5 /nobreak >nul
echo.
echo 🔐 Your Jenkins Admin Password:
echo ================================
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
echo.
echo ================================
echo Copy this password and use it in Jenkins setup!
echo.
pause
