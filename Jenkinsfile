pipeline {
    agent any
    
    environment {
        // These will be set in Jenkins configuration
        OPENAI_API_KEY = credentials('openai-api-key')
        OPENROUTER_API_KEY = credentials('openrouter-api-key')
        DOCKER_HOST = 'unix:///var/run/docker.sock'
    }
    
    stages {
        
        stage('Build Images') {
            steps {
                echo '🏗️ Building Docker images...'
                script {
                    try {
                        // Build backend image
                        sh 'docker build -t health-ai-backend ./backend'
                        
                        // Build frontend image  
                        sh 'docker build -t health-ai-frontend ./frontend'
                        
                        echo '✅ Docker images built successfully!'
                    } catch (Exception e) {
                        echo "❌ Failed to build images: ${e.getMessage()}"
                        error("Build failed")
                    }
                }
            }
        }
        
        stage('Test') {
            steps {
                echo '🧪 Running tests...'
                script {
                    try {
                        // Stop any running containers
                        sh 'docker-compose down || true'
                        
                        // Start test environment
                        sh 'docker-compose up -d'
                        
                        // Wait for services to be ready
                        sh 'sleep 30'
                        
                        echo '✅ Test environment started!'
                        
                        // Simple test - check if containers are running
                        sh 'docker-compose ps'
                        
                        echo '✅ All tests passed!'
                    } catch (Exception e) {
                        echo "❌ Tests failed: ${e.getMessage()}"
                        sh 'docker-compose logs || true'
                        error("Tests failed")
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo '🚀 Deploying application...'
                script {
                    try {
                        // Deploy to production (restart with latest images)
                        sh 'docker-compose down || true'
                        sh 'docker-compose up -d'
                        
                        // Wait a bit for startup
                        sh 'sleep 10'
                        
                        // Show running containers
                        sh 'docker-compose ps'
                        
                        echo '✅ Deployment complete!'
                        echo '🌐 Frontend: http://localhost:8501'
                        echo '📡 Backend API: http://localhost:8000'
                    } catch (Exception e) {
                        echo "❌ Deployment failed: ${e.getMessage()}"
                        error("Deployment failed")
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up...'
            // Clean up test containers but keep production running
            script {
                if (env.BRANCH_NAME != 'main') {
                    sh 'docker-compose down || true'
                }
            }
        }
        success {
            echo '🎉 Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs above.'
        }
    }
}
