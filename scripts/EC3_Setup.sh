#!/bin/bash
yum -y update
yum install -y ruby
yum install -y aws-cli
yum install -y python3
#Install code deploy into virtual machine
cd /home/ec2-user
wget https://aws-codedeploy-us-east-2.s3.us-east-2.amazonaws.com/latest/install
chmod +x ./install
sudo ./install auto