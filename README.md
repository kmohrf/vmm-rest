# vmm-rest

A REST-ish API for [vmm](http://vmm.localdomain.org/) the virtual mail manager.

vmm-rest is in the very early stages. Adding new domains or user accounts (anything that touches the filesystem) won’t work at the moment.


## Run vmm-rest

You can use the make target `make run` to start the flask debug server. This will try to execute
the application directly with python3 or – as a fallback – with pipenv. If neither works
install [pipenv](https://github.com/pypa/pipenv) or manually setup dependencies either with
your systems package manager or using virtualenv.

vmm-rest depends on the v0.7.x branch of vmm. `make run` will automatically setup the
correct branch for you in a local copy if you have installed mercurial.


## Routes

### Domains

GET    `/api/domains`
  : list all domains
  
POST   `/api/domains`
  : add a new domain
  
GET    `/api/domains/<name>`
  : display a specific domain

PUT    `/api/domains/<name>`
  : update domain data
  
DELETE `/api/domains/<name>`
  : delete a domain

### Users (Mailboxes)

GET    `/api/users`
  : list all users
  
POST   `/api/users`
  : add a new user
  
GET    `/api/users/<address>`
  : display a specific user

PUT    `/api/users/<address>`
  : update user data
  
DELETE `/api/users/<address>`
  : delete a user

### Aliases/ Forwards

GET    `/api/aliases`
  : list all aliases
  
POST   `/api/aliases`
  : add a new alias
  
GET    `/api/aliases/<address>`
  : display a specific alias

PUT    `/api/users/<address>`
  : update alias data
  
DELETE `/api/users/<address>`
  : delete an alias
