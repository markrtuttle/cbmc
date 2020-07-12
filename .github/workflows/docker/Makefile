# Call this makefile from the root of the cbmc repository
# make -f $(DIR)/Makefile DIR=$(DIR)

TAG ?= cbmc

ROOT ?= ../../..
DOCKER ?= .github/workflows/docker


default:
	cd $(ROOT) && docker build --tag $(TAG) --file $(DOCKER)/Dockerfile .


# tag with version
# push to docker hub

# make tools
