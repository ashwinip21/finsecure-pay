
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        IMAGE_REPO = 'ashwinip21/finsecure-pay'
        K8S_DEPLOYMENT = 'finsecure-pay'
        K8S_CONTAINER = 'finsecure-pay'
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
                    python3 -m venv .venv-ci
                    .venv-ci/bin/python -m pip install --upgrade pip
                    .venv-ci/bin/python -m pip install -r requirements.txt
                    .venv-ci/bin/python -m compileall -q app tests
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -eu
                    .venv-ci/bin/python -m pytest \
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

        stage('Security Checks') {
            steps {
                sh '''
                    set -eu
                    .venv-ci/bin/python -m pip install pip-audit
                    .venv-ci/bin/python -m pip_audit \
                        -r requirements.txt
                '''
            }
        }

        stage('Container Build') {
            steps {
                script {
                    env.IMAGE_TAG = "build-${env.BUILD_NUMBER}"
                }
                sh '''
                    set -eu
                    docker build \
                        --pull \
                        -t "$IMAGE_REPO:$IMAGE_TAG" \
                        -t "$IMAGE_REPO:latest" \
                        .
                    docker image inspect "$IMAGE_REPO:$IMAGE_TAG"
                '''
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu
                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin
                        docker push "$IMAGE_REPO:$IMAGE_TAG"
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Local Kubernetes') {
            steps {
                sh '''
                    set -eu

                    kubectl config use-context docker-desktop
                    kubectl apply -f k8s/configmap.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl set image \
                        deployment/"$K8S_DEPLOYMENT" \
                        "$K8S_CONTAINER"="$IMAGE_REPO:$IMAGE_TAG"

                    kubectl rollout status \
                        deployment/"$K8S_DEPLOYMENT" \
                        --timeout=180s

                    kubectl get deployment "$K8S_DEPLOYMENT"
                    kubectl get pods -l app=finsecure-pay
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set -eu
                    kubectl get deployment finsecure-pay \
                        -o jsonpath='{.spec.template.spec.containers[0].image}'
                    echo
                    kubectl rollout status deployment/finsecure-pay
                '''
            }
        }
    }

    post {
        success {
            echo 'FinSecure Pay pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Review the failed stage. Later stages were skipped.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
