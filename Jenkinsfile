pipeline {
    agent any

    stages {
        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t product-api .'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker rm -f product-api || true'
            }
        }

        stage('Run New Container') {
            steps {
                sh 'docker run -d -p 8000:8000 --name product-api product-api'
            }
        }

    }
}
