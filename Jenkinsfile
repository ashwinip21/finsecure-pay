
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

        stage('Code Quality - Ruff') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    .venv-ci/bin/python -m pip install ruff

                    .venv-ci/bin/python -m ruff check \
                        app tests \
                        --output-format json \
                        --output-file ruff-report.json

                    echo "Static analysis passed."
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
                        allowEmptyResults: true
                    )
                }
            }
        }

        stage('Dependency Vulnerability Audit') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    .venv-ci/bin/python -m pip install pip-audit

                    .venv-ci/bin/python -m pip_audit \
                        -r requirements.txt \
                        --format json \
                        --output dependency-audit-report.json

                    echo "Dependency vulnerability audit passed."
                '''
            }
        }

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

                    kubectl config use-context "$K8S_CONTEXT"
                    kubectl get nodes
                    kubectl get deployment "$K8S_DEPLOYMENT"

                    echo "Required tools are accessible."
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

                    echo "Building $IMAGE_REPO:$IMAGE_TAG"

                    docker build \
                        --pull \
                        -t "$IMAGE_REPO:$IMAGE_TAG" \
                        .

                    docker image inspect "$IMAGE_REPO:$IMAGE_TAG"

                    echo "Container image built successfully."
                '''
            }
        }

        stage('Container Image Security Scan - Trivy') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    IMAGE="$IMAGE_REPO:$IMAGE_TAG"
                    REPORT="trivy-image-report.txt"

                    echo "Scanning image: $IMAGE"
                    echo "Security policy: block HIGH and CRITICAL vulnerabilities."

                    # Generate a report and enforce the security gate.
                    # The report is printed even when the gate fails.
                    if trivy image \
                        --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --ignore-unfixed \
                        --exit-code 1 \
                        --format table \
                        --output "$REPORT" \
                        "$IMAGE"
                    then
                        SCAN_STATUS=0
                    else
                        SCAN_STATUS=$?
                    fi

                    if [ -f "$REPORT" ]; then
                        cat "$REPORT"
                    fi

                    if [ "$SCAN_STATUS" -ne 0 ]; then
                        echo "SECURITY GATE FAILED: HIGH/CRITICAL vulnerabilities detected, or the scan could not complete."
                        exit "$SCAN_STATUS"
                    fi

                    echo "Security gate passed."
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

                        # Ensure Docker logout is attempted even on failure.
                        trap 'docker logout >/dev/null 2>&1 || true' EXIT

                        printf '%s' "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin

                        docker push "$IMAGE_REPO:$IMAGE_TAG"

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
        always {
            junit(
                testResults: 'test-results.xml',
                allowEmptyResults: true
            )

            archiveArtifacts(
                artifacts: 'ruff-report.json,dependency-audit-report.json,trivy-image-report.txt,test-results.xml',
                allowEmptyArchive: true,
                fingerprint: true
            )

            echo 'Pipeline execution finished. Reports archived when generated.'
        }

        success {
            echo 'FinSecure Pay CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check the stage logs and archived security reports. Later stages are skipped after a failure.'
        }
    }
}
