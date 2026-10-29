
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
        K8S_CONTEXT = 'docker-desktop'
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
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    PYTHON_BIN=/opt/homebrew/bin/python3.12

                    "$PYTHON_BIN" --version

                    rm -rf .venv-ci
                    "$PYTHON_BIN" -m venv .venv-ci

                    .venv-ci/bin/python -m pip install --upgrade pip
                    .venv-ci/bin/python -m pip install -r requirements.txt

                    .venv-ci/bin/python -m compileall -q app tests

                    echo "Build completed successfully."
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    .venv-ci/bin/python -m pytest \
                        -v \
                        --junitxml=test-results.xml
                '''
            }

            post {
                always {
                    junit(
                        testResults: 'test-results.xml',
                        allowEmptyResults: false
                    )
                }
            }
        }

        stage('Security Checks') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    .venv-ci/bin/python -m pip install pip-audit

                    .venv-ci/bin/python -m pip_audit \
                        -r requirements.txt

                    echo "Dependency security audit completed."
                '''
            }
        }

        stage('Check Deployment Tools') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    echo "Checking Docker CLI..."
                    command -v docker
                    docker --version
                    docker info >/dev/null
                    echo "Docker daemon is accessible."

                    echo "Checking Kubernetes CLI..."
                    command -v kubectl
                    kubectl version --client

                    kubectl config get-contexts
                    kubectl config use-context "$K8S_CONTEXT"
                    kubectl get nodes

                    kubectl get deployment "$K8S_DEPLOYMENT"
                    echo "Deployment tools are accessible."
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
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    echo "Building image: $IMAGE_REPO:$IMAGE_TAG"

                    docker build \
                        --pull \
                        -t "$IMAGE_REPO:$IMAGE_TAG" \
                        .

                    docker image inspect "$IMAGE_REPO:$IMAGE_TAG"

                    echo "Container image built successfully."
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
                        export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin

                        docker push "$IMAGE_REPO:$IMAGE_TAG"

                        docker logout

                        echo "Image pushed successfully."
                    '''
                }
            }
        }

        stage('Deploy to Local Kubernetes') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    kubectl config use-context "$K8S_CONTEXT"

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
                    kubectl get service finsecure-pay-service

                    echo "Kubernetes deployment completed."
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    kubectl config use-context "$K8S_CONTEXT"

                    echo "Deployed image:"
                    kubectl get deployment "$K8S_DEPLOYMENT" \
                        -o jsonpath='{.spec.template.spec.containers[0].image}'
                    echo

                    kubectl rollout status \
                        deployment/"$K8S_DEPLOYMENT" \
                        --timeout=180s

                    kubectl get deployment "$K8S_DEPLOYMENT"
                    kubectl get pods -l app=finsecure-pay

                    echo "Deployment verification completed."
                '''
            }
        }
    }

    post {
        success {
            echo 'FinSecure Pay CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Review the failed stage. Later stages should be skipped.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
