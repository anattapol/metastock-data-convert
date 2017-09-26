pipeline {
    agent any

    environment {
        FOO = "BAR"
    }

    stages {
        def RSYNC_DEST = './metastock-data/'
        def RSYNC_SRC = 'rsync://darthvader@176.32.89.130'
        def CDC_PASS = '/var/lib/jenkins/rsync_pass'

        stage('Download MS Data') {
            sh "mkdir -p ${RSYNC_DEST}"
            sh "rsync --password-file=${CDC_PASS} -avz ${RSYNC_SRC}/msd/SET/ ${RSYNC_DEST}/SET/"
        }

        stage('Checkout SCM') {
            checkout scm
        }

        stage('Convert to CSV') {
            sh "python3 ms2txt.py -a -i ${RSYNC_DEST}/SET/ -o"
        }
    }


    post {
        always {
        }

        success {
        }

        failure {
        }
    }
}
