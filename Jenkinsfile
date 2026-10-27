
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checked out successfully.'
            }
        }

        stage('Build') {
            steps {
                sh '''
                    set -eu
                    python3 --version
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/python -m pip install -r requirements.txt
                    .venv/bin/python -m compileall -q app tests
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -eu
                    .venv/bin/python -m pytest \
                        -v \
                        --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit testResults: 'test-results.xml',
                          allowEmptyResults: false
                }
            }
        }

        stage('Check Deployment Tools') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
                    docker --version
                    docker info
                    kubectl config current-context
                    kubectl get deployment finsecure-pay
                '''
            }
        }
    }

    post {
        success {
            echo 'FinSecure Pay CI checks passed.'
        }
        failure {
            echo 'Pipeline failed. Review the stage logs before proceeding.'
        }
    }
}
