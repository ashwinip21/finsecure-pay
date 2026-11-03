
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        // Docker Hub configuration
        IMAGE_REPO = 'ashwinip21/finsecure-pay'

        // Kubernetes deployment configuration
        K8S_DEPLOYMENT = 'finsecure-pay'
        K8S_CONTAINER = 'finsecure-pay'

        // AWS EKS configuration
        AWS_REGION = 'ap-southeast-1'
        EKS_CLUSTER = 'finsecure-pay-cluster'

        K8S_CONTEXT = 'arn:aws:eks:ap-southeast-1:112859066331:cluster/finsecure-pay-cluster'
    }

    stages {

        // ==========================================
        // 1. CHECKOUT
        // ==========================================

        stage('Checkout') {
            steps {
                checkout scm
                sh 'mkdir -p security-reports'
            }
        }

        // ==========================================
        // 2. VERIFY JENKINS AWS ENVIRONMENT
        // ==========================================

        stage('Verify Jenkins AWS and EKS Access') {
            steps {
                sh '''
                    set -eu

                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    echo "=========================================="
                    echo "JENKINS ENVIRONMENT VERIFICATION"
                    echo "=========================================="

                    echo "Jenkins user:"
                    whoami

                    echo "Home directory:"
                    echo "$HOME"

                    echo "AWS CLI:"
                    command -v aws
                    aws --version

                    echo "Verifying AWS identity:"
                    aws sts get-caller-identity

                    echo "Updating EKS kubeconfig:"
                    aws eks update-kubeconfig \
                        --region "$AWS_REGION" \
                        --name "$EKS_CLUSTER"

                    echo "Switching to AWS EKS context:"
                    kubectl config use-context "$K8S_CONTEXT"

                    echo "Verifying Kubernetes cluster:"
                    kubectl cluster-info

                    echo "Verifying EKS worker nodes:"
                    kubectl get nodes -o wide

                    echo "Docker version:"
                    docker --version

                    echo "Docker daemon verification:"
                    docker info >/dev/null

                    echo "kubectl version:"
                    kubectl version --client

                    echo "=========================================="
                    echo "AWS EKS ACCESS VERIFIED"
                    echo "=========================================="
                '''
            }
        }

        // ==========================================
        // 3. BUILD APPLICATION
        // ==========================================

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

                    echo "Application build completed."
                '''
            }
        }

        // ==========================================
        // 4. CODE QUALITY - RUFF
        // ==========================================

        stage('Code Quality - Ruff') {
            steps {
                sh '''
                    set -eu

                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    .venv-ci/bin/python -m pip install ruff

                    .venv-ci/bin/python -m ruff check \
                        app tests \
                        --output-format json \
                        --output-file security-reports/ruff-report.json

                    echo "Ruff code quality check passed."
                '''
            }
        }

        // ==========================================
        // 5. AUTOMATED TESTING
        // ==========================================

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
                          allowEmptyResults: true
                }
            }
        }

        // ==========================================
        // 6. DEPENDENCY VULNERABILITY AUDIT
        // ==========================================

        stage('Dependency Vulnerability Audit') {
            steps {
                sh '''
                    set -eu

                    .venv-ci/bin/python -m pip install pip-audit

                    set +e

                    .venv-ci/bin/python -m pip_audit \
                        -r requirements.txt \
                        --format json \
                        --output security-reports/dependency-audit-report.json

                    AUDIT_STATUS=$?

                    set -e

                    if [ "$AUDIT_STATUS" -ne 0 ]; then
                        echo "Dependency audit failed."
                        exit "$AUDIT_STATUS"
                    fi

                    echo "Dependency audit passed."
                '''
            }
        }

        // ==========================================
        // 7. CHECK DEPLOYMENT TOOLS AND EKS
        // ==========================================

        stage('Check Deployment Tools') {
            steps {
                sh '''
                    set -eu

                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    echo "Checking Docker..."
                    command -v docker
                    docker --version
                    docker info >/dev/null

                    echo "Checking kubectl..."
                    command -v kubectl
                    kubectl version --client

                    echo "Checking Trivy..."
                    command -v trivy
                    trivy --version

                    echo "Checking AWS identity..."
                    aws sts get-caller-identity

                    echo "Updating EKS kubeconfig..."

                    aws eks update-kubeconfig \
                        --region "$AWS_REGION" \
                        --name "$EKS_CLUSTER"

                    kubectl config use-context "$K8S_CONTEXT"

                    echo "Checking EKS nodes..."
                    kubectl get nodes

                    echo "Checking Kubernetes namespace..."
                    kubectl get namespace default

                    echo "Deployment tools and EKS checks passed."
                '''
            }
        }

        // ==========================================
        // 8. CONTAINER BUILD - AMD64 FOR AWS EKS
        // ==========================================

        stage('Container Build') {
            steps {
                script {
                    env.IMAGE_TAG = "build-${env.BUILD_NUMBER}"
                }

                sh '''
                    set -eu

                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    echo "=========================================="
                    echo "BUILDING DOCKER IMAGE FOR AWS EKS"
                    echo "Target architecture: linux/amd64"
                    echo "=========================================="

                    docker build --platform linux/amd64 --pull \
                        -t "$IMAGE_REPO:$IMAGE_TAG" .

                    docker image inspect "$IMAGE_REPO:$IMAGE_TAG"

                    echo "Verifying image architecture..."

                    docker image inspect "$IMAGE_REPO:$IMAGE_TAG" \
                        --format '{{.Os}}/{{.Architecture}}'

                    echo "Docker image built successfully."
                '''
            }
        }

        // ==========================================
        // 9. TRIVY CONTAINER IMAGE SECURITY SCAN
        // ==========================================

        stage('Container Image Security Scan - Trivy') {
            steps {
                sh '''
                    set -eu

                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    IMAGE="$IMAGE_REPO:$IMAGE_TAG"

                    mkdir -p security-reports

                    REPORT="security-reports/trivy-image-report.txt"
                    JSON_REPORT="security-reports/trivy-image-report.json"

                    echo "=========================================="
                    echo "TRIVY CONTAINER IMAGE SECURITY SCAN"
                    echo "Image: $IMAGE"
                    echo "Severity: HIGH, CRITICAL"
                    echo "Ignore unfixed: enabled"
                    echo "=========================================="

                    trivy image \
                        --scanners vuln \
                        --format json \
                        --output "$JSON_REPORT" \
                        "$IMAGE"

                    set +e

                    trivy image \
                        --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --ignore-unfixed \
                        --exit-code 1 \
                        --format table \
                        --output "$REPORT" \
                        "$IMAGE"

                    SCAN_STATUS=$?

                    set -e

                    echo "========== TRIVY RESULTS =========="

                    if [ -f "$REPORT" ]; then
                        cat "$REPORT"
                    fi

                    if [ "$SCAN_STATUS" -ne 0 ]; then
                        echo "SECURITY GATE FAILED."
                        echo "Review security-reports/trivy-image-report.txt"
                        exit "$SCAN_STATUS"
                    fi

                    echo "Security gate passed."
                    echo "No unfixed HIGH/CRITICAL findings."
                '''
            }
        }

        // ==========================================
        // 10. PUSH IMAGE TO DOCKER HUB
        // ==========================================

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

                        trap 'docker logout >/dev/null 2>&1 || true' EXIT

                        printf '%s' "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin

                        docker push "$IMAGE_REPO:$IMAGE_TAG"

                        echo "Docker image pushed successfully."
                    '''
                }
            }
        }

        // ==========================================
        // 11. DEPLOY TO AWS EKS
        // ==========================================

        stage('Deploy to AWS EKS') {
            steps {
                sh '''
                    set -eu

                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    echo "Connecting to AWS EKS..."

                    aws eks update-kubeconfig \
                        --region "$AWS_REGION" \
                        --name "$EKS_CLUSTER"

                    kubectl config use-context "$K8S_CONTEXT"

                    echo "Applying ConfigMap..."
                    kubectl apply -f k8s/configmap.yaml

                    echo "Applying Kubernetes Service..."
                    kubectl apply -f k8s/service.yaml

                    echo "Applying Kubernetes Deployment..."
                    kubectl apply -f k8s/deployment.yaml

                    echo "Updating application image..."

                    kubectl set image \
                        deployment/"$K8S_DEPLOYMENT" \
                        "$K8S_CONTAINER"="$IMAGE_REPO:$IMAGE_TAG"

                    echo "Waiting for successful EKS rollout..."

                    kubectl rollout status \
                        deployment/"$K8S_DEPLOYMENT" \
                        --timeout=180s

                    echo "EKS deployment completed."

                    kubectl get deployment "$K8S_DEPLOYMENT"

                    kubectl get pods -l app=finsecure-pay

                    kubectl get service finsecure-pay-service
                '''
            }
        }

        // ==========================================
        // 12. VERIFY AWS EKS DEPLOYMENT
        // ==========================================

        stage('Verify EKS Deployment') {
            steps {
                sh '''
                    set -eu

                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    aws eks update-kubeconfig \
                        --region "$AWS_REGION" \
                        --name "$EKS_CLUSTER"

                    kubectl config use-context "$K8S_CONTEXT"

                    echo "=========================================="
                    echo "VERIFYING FINSECURE PAY ON AWS EKS"
                    echo "=========================================="

                    echo "Deployed image:"

                    kubectl get deployment "$K8S_DEPLOYMENT" \
                        -o jsonpath='{.spec.template.spec.containers[0].image}'

                    echo

                    echo "Rollout status:"

                    kubectl rollout status \
                        deployment/"$K8S_DEPLOYMENT" \
                        --timeout=180s

                    echo "Deployment details:"

                    kubectl get deployment "$K8S_DEPLOYMENT"

                    echo "Application pods:"

                    kubectl get pods -l app=finsecure-pay -o wide

                    echo "Kubernetes services:"

                    kubectl get services

                    echo "=========================================="
                    echo "FINSECURE PAY EKS DEPLOYMENT VERIFIED"
                    echo "=========================================="
                '''
            }
        }
    }

    // ==========================================
    // POST BUILD ACTIONS
    // ==========================================


    post {

        always {
            junit testResults: 'test-results.xml',
                allowEmptyResults: true

            archiveArtifacts(
                artifacts: 'security-reports/**,test-results.xml',
                allowEmptyArchive: true,
                fingerprint: true
            )

            echo 'FinSecure Pay pipeline execution finished.'
        }

        success {
            echo 'FinSecure Pay AWS EKS CI/CD pipeline completed successfully.'

            emailext(
                to: 'ashwini.p21@gmail.com',
                subject: "FinSecure Pay - Build SUCCESS - #${BUILD_NUMBER}",
                mimeType: 'text/html',
                body: """
                    <h2>FinSecure Pay CI/CD Pipeline</h2>
                    <p><b>Project:</b> finsecure-pay-pipeline</p>
                    <p><b>Build Number:</b> ${BUILD_NUMBER}</p>
                    <p><b>Build Status:</b> SUCCESS</p>
                    <p><b>Repository:</b> ashwinip21/finsecure-pay</p>
                    <p><b>Build URL:</b>
                    <a href="${BUILD_URL}">${BUILD_URL}</a></p>
                    <p>The FinSecure Pay pipeline completed successfully.</p>
                """
            )
        }

        failure {
            echo 'Pipeline failed. Review the failed stage and archived reports.'

            emailext(
                to: 'ashwini.p21@gmail.com',
                subject: "FinSecure Pay - Build FAILURE - #${BUILD_NUMBER}",
                mimeType: 'text/html',
                body: """
                    <h2>FinSecure Pay CI/CD Pipeline</h2>
                    <p><b>Project:</b> finsecure-pay-pipeline</p>
                    <p><b>Build Number:</b> ${BUILD_NUMBER}</p>
                    <p><b>Build Status:</b> FAILURE</p>
                    <p><b>Build URL:</b>
                    <a href="${BUILD_URL}">${BUILD_URL}</a></p>
                    <p>Please review the failed pipeline stage.</p>
                """
            )
        }
    }

