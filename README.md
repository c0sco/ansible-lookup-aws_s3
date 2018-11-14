# ansible-lookup-aws_s3

AWS S3 lookup plugin for Ansible

## Installation

Ansible-galaxy can be used for installation.

```bash
ansible-galaxy install git+https://github.com/c0sco/ansible-lookup-aws_s3
```

This requires the role `ansible-lookup-aws_s3` be included in your playbook. Otherwise, install the aws_s3.py file in the lookup plugins directory you have configured in ansible.cfg.

## Lookup plugin

Use `lookup()` with the `aws_s3` argument, followed by the URLs you want to retrieve. Boto profiles are used to connect to S3 with the default profile being used unless `profile` is specified. Multiple S3 URLs can be provided, the contents will be concatenated together.

For example:

```yaml
# Get contents of YAML files in S3
- debug: msg="{{ lookup('aws_s3', 's3://my-bucket/myinfo.yml', 's3://my-other-bucker/thing.yml', profile='myawsbotoprofile') }}"
```

If you want to run the plugin directly for testing, you can supply S3 URLs on the command line. The default boto profile will be used.

```bash
aws_s3.py s3://s3-bucket/stuff.txt
```
