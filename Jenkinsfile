
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
                sh 'mkdir -p security-reports'
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
                        --output-file security-reports/ruff-report.json
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
                          allowEmptyResults: true
                }
            }
        }

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
                        echo "Dependency audit failed. Review the JSON report."
                        exit "$AUDIT_STATUS"
                    fi

                    echo "Dependency audit passed."
                '''
            }
        }

        stage('Check Deployment Tools') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    command -v docker
                    docker --version
                    docker info >/dev/null

                    command -v kubectl
                    kubectl version --client

                    command -v trivy
                    trivy --version

                    kubectl config use-context "$K8S_CONTEXT"
                    kubectl get nodes
                    kubectl get deployment "$K8S_DEPLOYMENT"
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

                    docker build --pull \
                        -t "$IMAGE_REPO:$IMAGE_TAG" .

                    docker image inspect "$IMAGE_REPO:$IMAGE_TAG"
                '''
            }
        }

        stage('Container Image Security Scan - Trivy') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    IMAGE="$IMAGE_REPO:$IMAGE_TAG"
                    REPORT="security-reports/trivy-image-report.txt"
                    JSON_REPORT="security-reports/trivy-image-report.json"

                    # Always create a full vulnerability report first.
                    trivy image \
                        --scanners vuln \
                        --format json \
                        --output "$JSON_REPORT" \
                        "$IMAGE"

                    # Enforce the HIGH/CRITICAL security gate.
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

                    if [ -f "$REPORT" ]; then
                        cat "$REPORT"
                    fi

                    if [ "$SCAN_STATUS" -ne 0 ]; then
                        echo "Security gate failed or scan could not complete."
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

                        trap 'docker logout >/dev/null 2>&1 || true' EXIT

                        printf '%s' "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin

                        docker push "$IMAGE_REPO:$IMAGE_TAG"
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
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set -eu
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    kubectl config use-context "$K8S_CONTEXT"

                    kubectl get deployment "$K8S_DEPLOYMENT" \
                        -o jsonpath='{.spec.template.spec.containers[0].image}'
                    echo

                    kubectl rollout status \
                        deployment/"$K8S_DEPLOYMENT" \
                        --timeout=180s

                    kubectl get deployment "$K8S_DEPLOYMENT"
                    kubectl get pods -l app=finsecure-pay
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'test-results.xml',
                  allowEmptyResults: true

            archiveArtifacts(
                artifacts: 'security-reports/**,test-results.xml',
                allowEmptyArchive: false,
                fingerprint: true
            )

            echo 'Pipeline execution finished.'
        }
        success {
            echo 'FinSecure Pay CI/CD pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Review the failed stage and archived reports.'
        }
    }
}
