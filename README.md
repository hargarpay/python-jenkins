# JENKINS JOBS STATUS
This script is about getting a job from jenkins api and store the build status of the job in the Jenkins API in sqlite database.

## CREDIENTIALS
To use the python script, the following need to to be store in a .env file.

> The SCHEMA can be either http:// or https://.
> If the Jenkins API has SSL then use https://, if not use http://
<br>
SCHEMA=
<br>
> The domain name of the Jenkins API eg jenkins.test:8080
<br>
> without the schema(http:// or https://)
<br>
DOMAIN_NAME=
<br>
> The username of the jenkins API
<br>
USERNAME=
<br>
> The [api key](https://jenkins.io/blog/2018/07/02/new-api-token-system/) of the Jenkins API.

API_KEY=

**Rename the .env-example to .env and fill the variables.**