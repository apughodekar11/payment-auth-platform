pipeline {
    agent any

    environment {
        // Edit these two:
        ECR        = '464535293192.dkr.ecr.eu-west-1.amazonaws.com/payment-auth'
        AWS_REGION = 'eu-west-1'
        IMAGE      = "${ECR}:${BUILD_NUMBER}"   
    }

    stages {
        stage('Test') {
            // If the unit tests fail. Cheapest gate first.
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -q -r requirements.txt
                    python -m pytest tests/ -q
                '''
            }
        }

        stage('Build & Push') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION \
                      | docker login --username AWS --password-stdin ${ECR%/*}
                    docker build -t $IMAGE -t $ECR:latest .
                    docker push $IMAGE
                    docker push $ECR:latest
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    kubectl set image deployment/payment-auth payment-auth=$IMAGE
                    kubectl rollout status deployment/payment-auth --timeout=120s
                '''
            }
        }

        stage('Smoke test') {
            // Hit the service through a temporary port-forward and confirm it answers.
            steps {
                sh '''
                    # Start port-forward in background, capture its PID, and make sure
                    # we always kill it even if the curl fails (trap on EXIT).
                    kubectl port-forward svc/payment-auth 18080:80 > /tmp/pf.log 2>&1 &
                    PF_PID=$!
                    trap "kill $PF_PID 2>/dev/null || true" EXIT

                    # Wait until the port actually answers, up to ~20s, instead of a blind sleep.
                    for i in $(seq 1 20); do
                        if curl -fsS localhost:18080/healthz 2>/dev/null; then
                            echo "smoke test passed"
                            exit 0
                        fi
                        sleep 1
                    done

                    echo "smoke test failed - service did not respond"
                    cat /tmp/pf.log
                    exit 1
                '''
            }
        }
    }

    post {
        failure {
            // Any stage failing lands here. Roll the deployment back to the
            // previous revision - this is the bullet's headline behaviour.
            echo 'Pipeline failed - rolling back to previous version.'
            sh 'kubectl rollout undo deployment/payment-auth || true'
        }
        success {
            echo 'Deployed and smoke-tested successfully.'
        }
    }
}
