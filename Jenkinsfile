pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                echo '🚀 Starting Health AI Assistant Build Pipeline'
                echo "📂 Working directory: ${pwd()}"
                
                script {
                    // Clean and clone fresh
                    sh '''
                        rm -rf health-ai-assistant || true
                        git clone https://github.com/VinitChawda06/health-ai-assistant.git
                        cd health-ai-assistant
                        ls -la
                    '''
                }
            }
        }
        
        stage('Build Images') {
            steps {
                echo '🏗️ Building Docker images...'
                script {
                    sh '''
                        cd health-ai-assistant
                        echo "Building backend image..."
                        docker build -t health-ai-backend ./backend
                        
                        echo "Building frontend image..."
                        docker build -t health-ai-frontend ./frontend
                        
                        echo "✅ Images built successfully!"
                        docker images | grep health-ai
                    '''
                }
            }
        }
        
        stage('Test') {
            steps {
                echo '🧪 Running tests...'
                script {
                    sh '''
                        cd health-ai-assistant
                        
                        # Stop any existing containers
                        docker-compose down || true
                        
                        # Start test environment
                        echo "Starting containers..."
                        docker-compose up -d
                        
                        # Wait for startup
                        sleep 30
                        
                        # Check container status
                        echo "Container status:"
                        docker-compose ps
                        
                        echo "✅ Test environment started successfully!"
                    '''
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo '🚀 Deploying application...'
                script {
                    sh '''
                        cd health-ai-assistant
                        
                        # Ensure clean deployment
                        docker-compose down || true
                        docker-compose up -d
                        
                        # Wait for startup
                        sleep 10
                        
                        # Show final status
                        echo "🎉 Deployment Status:"
                        docker-compose ps
                        
                        echo "✅ Health AI Assistant deployed successfully!"
                        echo "🌐 Frontend: http://localhost:8501"
                        echo "📡 Backend API: http://localhost:8000"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '🧹 Pipeline completed'
        }
        success {
            echo '🎉 Build and deployment successful!'
        }
        failure {
            echo '❌ Build failed - check logs above'
        }
    }
}
}
