# scanecr

Enable basic scanning of Amazon ECR for Common Vulnerabilities and Exposures (CVEs) from the open-source Clair project.

A custom resource initially runs, enabling basic scanning on all ECR repositories in every region of the deployed account.

Basic scans are completed daily for every image in all repositories. On-push scans count against the daily quota of one per day, which will result in an error.
