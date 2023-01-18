# scanecr

Enable basic scanning of Amazon ECR for Common Vulnerabilities and Exposures (CVEs) from the open-source Clair project.

A custom resource initially runs, enabling basic scanning on the private registry since ScanOnPush configuration at the repository level is deprecated.

Basic scans are completed daily for every image in all repositories in the deployed region. On-push scans count against the daily quota of one per day, which will result in an error.
