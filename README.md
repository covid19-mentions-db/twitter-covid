# twitter-covid

<b>REQUIRED ENVIRONMENT VARIABLES</b>

\# Mongo DB to store posts
- `MONGODB_HOST`
- `MONGODB_PORT`
- `MONGODB_DB`
- `MONGODB_USER`
- `MONGODB_PASSWORD`
- `MONGODB_AUTH_DB`
- `MONGODB_RESULT_COLLECTION` - collection to store posts  
- `MONGODB_TASK_COLLECTION` - collection to store completed tasks

\# RabbitMQ to distribute tasks
- `RABBITMQ_HOST`
- `RABBITMQ_PORT`
- `RABBITMQ_USER`
- `RABBITMQ_PASSWORD`
- `RABBITMQ_QUEUE`

\# Proxy settings  
- `PROXIES_FILE_PATH_OR_URL` - may be url(calling it gives a list of proxies), filepath, empty(proxy won't be used)  
- `PROXIES_TYPE` - http(s), socks5, empty(when proxy is not used)  
 
\# If you use gitlab ci/cd(.gitlab-ci.yml is in the project) + kubernetes, you should also define:  
- `K8S_SERVER` - K8S api URL  
- `K8S_CERT` - K8S certificate  
- `K8S_TOKEN` - K8S token  
- `MOUNT_CONTAINER_PATH` - if PROXIES_FILE_PATH_OR_URL is filepath    
- `MOUNT_HOST_PATH` - if PROXIES_FILE_PATH_OR_URL is filepath, path in your kubernetes host  
## How to start parsing from scratch + specific ENVIRONMENT VARIABLES
- <b>add_tasks_initial.py</b> - add tasks(dirrferent keywords, dates and so on) to RabbitMQ
- <b>consumer-twitter-advanced-search_api.py</b> - worker, executes(parses twits) tasks from RabbitMQ
- <b>job_task.py</b> - parses twits for every specified keywords, languages for last `DAYS_COUNT` days, keeps data up to date
    - `DAYS_COUNT` (default - 3)
