import calendar
import time

from github import Github
from github.GithubException import RateLimitExceededException, UnknownObjectException, BadCredentialsException
from requests import ReadTimeout


# Authorize the user to access Github for making requests
class GithubAuthorizor:
    # initialize GithubAuthorizor class
    def __init__(self, access_token):
        self.access_token = access_token
        self.is_authorized = True

    # get the user access token verified from github and return the rate limit for the authorization type
    def get_authorization_token(self):
        github_token = Github(self.access_token)
        try:
            print("Rate limit: " + str(github_token.get_rate_limit().core.limit))
        except BadCredentialsException:
            print("Incorrect access token. We will continue with unauthorized request. Unauthorized requests are slow. "
                  "If you wish to retry the access token then please quit the script execution")
            github_token = Github()
            print("Rate limit: " + str(github_token.get_rate_limit().core.limit))
            self.is_authorized = False

        return github_token, self.is_authorized

    # call get_authorization_token to get github access token and status. Then get github user based on authentication
    def get_github_user(self, github_username):
        github_token, is_user_authorized = self.get_authorization_token()
        github_user = github_token.get_user(github_username)

        return github_token, github_user, is_user_authorized


# Write list of commit for all branches in the separate text files
class CommitListWriter:
    # Initializing CommitListWriter class
    def __init__(self, is_authorized_request, github_token, github_user, list_branch):
        self.is_authorized_request = is_authorized_request
        self.github_token = github_token
        self.github_user = github_user
        self.list_branch = list_branch
        self.branch_sha_dict = {}

    # loop through all branches in a repo to get commit objects for each branch. Calling write_commit_list_to_file() for each branch
    def loop_through_branches(self):
        for current_branch in self.list_branch:
            self.branch_sha_dict[current_branch] = []
            commits_obj = self.github_user.get_repo(repo_name).get_commits(current_branch)
            self.write_commit_list_to_file(commits_obj, current_branch)

        return self.branch_sha_dict

    # writing commit list of a branch to file for which method was called
    def write_commit_list_to_file(self, commits, current_branch_name):
        start_row_num = 0
        loop_incomplete = True
        while loop_incomplete:
            print("Executing... Please be patient")
            try:
                with open(f"output/sha_list_{current_branch_name}.txt", mode='a+') as file:
                    file.write(current_branch_name + " " + str(commits.totalCount) + '\n')
                    for i in range(start_row_num, commits.totalCount):
                        fetched_sha = commits[i].sha
                        self.branch_sha_dict[current_branch_name].append(fetched_sha)
                        file.write(fetched_sha + '\n')

                        '''Please beware that github limits the rate of queries an ip can make in order to prevent web 
                        scraping abuse etc. https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting
                        adding 60 seconds for unauthorized requests to maintain rate of 60 requests/hour and 2 seconds 
                        for maintaining 5000 requests/hour'''
                        if self.is_authorized_request:
                            time.sleep(2)
                        else:
                            time.sleep(60)

                        if i == commits.totalCount - 1:
                            loop_incomplete = False

            except (RateLimitExceededException, ReadTimeout, ConnectionResetError) as e:
                print(f"Exception occurred: {e}. Waiting...")
                search_rate_limit = self.github_token.get_rate_limit().search
                reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
                # add 60 seconds to be sure the rate limit has been reset
                sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 60
                time.sleep(sleep_time)
                start_row_num = i - 1
                continue


# Compare the branches in round robin fashion and write the list of uniques SHAs to a file
class CommitListComparator:
    # Initializing BranchComparison class
    def __init__(self, commit_list_dict):
        self.commit_list_dict = commit_list_dict

    # Comparing branches in a round robin fashion to find the list unique commits in branch x as compared to y(set(commit list of branc x)-set(commit list of branc y))
    def list_of_unique_commits(self):
        for key_item in self.commit_list_dict.keys():
            self.commit_list_dict[key_item] = set(self.commit_list_dict[key_item])

        for key in self.commit_list_dict.keys():
            temp = self.commit_list_dict[key]
            with open("output/branch_comparison.txt", mode='a+') as file:
                for key_compare in self.commit_list_dict.keys():
                    file.write(
                        f"\nList of commits present in branch {key} but not in {key_compare} --> \n{temp - self.commit_list_dict[key_compare]}")


if __name__ == "__main__":
    list_branch_names = []  # Store name of all branches in a list
    list_commit_object = []  # List of commit objects for each branch
    github_access_token = None  # Default login username/password
    is_authorized = False  # By default not authorized

    # Get Github username and repo name
    github_username = input("Please enter Github username: ")
    repo_name = input("Please enter repository name: ")

    # Get input to know if request being made is authorized or unauthorized
    authorized = input("Would you like to make authorized request(y/n)? "
                       "If yes, please keep your Github access token ready: ")

    # Making sure script gets correct input from the user
    while True:
        if not authorized.isalpha():
            authorized = input("Entered value is incorrect. Would you like to make authorized request(y/n)?")
        elif authorized.isalpha():
            if authorized.capitalize() == "Y":
                github_access_token = input("Please enter your Github access token: ")
            elif authorized.capitalize() == "N":
                print("Ok we will proceed with unauthorized request")
            else:
                print('Please select either "y" or "n"')
                authorized = input("Entered value is incorrect. Would you like to make authorized request(y/n)?")
                continue
        break

    # Call get_github_user method from class Authorize.
    # Returns github access object, current user object and authorization status in boolean
    authorize_obj = GithubAuthorizor(github_access_token)
    token, user, is_authorized = authorize_obj.get_github_user(github_username)

    # Fetch the list of available branches. Catch exception in case user or repo is incorrect
    try:
        for branch in user.get_repo(repo_name).get_branches():
            list_branch_names.append(branch.name)
    except UnknownObjectException:
        print("Oh no! looks like either user or repository entered by you does not exist. "
              "Please try again with correct user and repo name.")

    # Calling loop_through_branches method of WriteShaToFile class.
    # Returns commit dictionary in the format {'branch1':[sha1, sha2, sha3], 'branch2':[sha1, sha2, sha3]}
    # Writes list of all commit SHAs to file sha_list_BranchName.txt
    write_to_file_obj = CommitListWriter(is_authorized, token, user, list_branch_names)
    commit_dict = write_to_file_obj.loop_through_branches()

    # Calling list_of_unique_commits method of BranchComparison class
    # Writes to branch_comparison.txt file, list of unique commits
    branch_comparison_obj = CommitListComparator(commit_dict)
    branch_comparison_obj.list_of_unique_commits()

    print("Done!")
