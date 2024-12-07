UPDATE public.user SET enabled_features = '{"cwaiapi": false, "daasapi": true, "faasapi": true, "auto_pay": false, "billable": false, "emailapi": false, "monitorapi": true, "k8sapi": true, "without_vat": false, "disable_emails": false, "iotapi": false, "emailapi": true}'
WHERE email = 'sre-devops@comwork.io';
