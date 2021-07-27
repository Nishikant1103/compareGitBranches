# Simple script to fetch SHA list of commits from git repo of a username and compare the branches to fetch unique commits

In this case the script has been written to run on any repo on Github.

**Input:**

1. Github username e.g. pallets     -->> Mandatory
2. Repository name e.g. markupsafe  -->> Mandatory
3. Github access token -->> Optional but recommended for higher request rate

**Output:**
1. SHA list files for each branch in the repo
2. File with unique SHA list 


**Limitations:**

As github limits the rate of query made by a remote client, this script can make maximum 600 requests/hour for unauthorized request and 5000 requests/hour with authorized request. That means its necessary to add sleep to maintain the rate of requests. 
On exceeding the rate-limit RateLimitExceededException is raised that is handled in the script.