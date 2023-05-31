<h2 id="ixia-upgrade-utility">Ixia Upgrade Utility</h2>
<hr>
<p>This python based tool will help customer upgrade their Linux bases IxOS Chassis in an automated way and at scale.</p>
<p>Before running this tool customer needs to identify</p>
<ol>
<li><p>Controller Chassis - Chassis where the customer will upload the upgrade version .tgz</p>
</li>
<li><p>Target Chassis - Chassis that need to be upgraded to a version whose .tgz was uploaded to Controller Chassis</p>
</li>
</ol>
<p>Next,  add the entries in config.py files in this repo. There is a sample config already present in there.</p>
<p>Upload the .tgz version you wish to upgrade to, on your controller chassis using SFTP. </p>

Before running the script, `pip install -r requirments.txt`
<h1 id="sample-output">Sample Output</h1>
<pre><code class="language-python">
(base) ashwjosh@C0HD4NKHCX ixupgradeutility % /usr/local/bin/python3 /Users/ashwjosh/ixupgradeutility/controller.py
INFO:root:Controller Chassis is 10.36.236.121 with username : admin and password : Kimchi123Kimchi123!
INFO:root:===== Fetching exisiting upgrade packages present on Controller Chassis 10.36.236.121
ID - VERSION
1 - 9.20.2700.12
2 - 9.30.3001.12
Please enter ID of version you want to upgeade to: 
2
You have selected to update target chassis to ID: 2. Please enter [Y/y] to proceed or [N/n] to re-enter: y
INFO:root:===== Adding Target Chassis from config file on Controller Chassis 10.36.236.121
Polling for async operation ...
Completed async operation
INFO:root:===== Target Chassis added on Controller Chassis 10.36.236.121. Please check at https://10.36.236.121/chassislab/chassisui/settings/ixos-install
INFO:root:===== Consolidating chassis credentials and target chassis id&#39;s added in previous step
INFO:root:[{&#39;id&#39;: 22, &#39;ip&#39;: &#39;10.36.237.131&#39;, &#39;activeVersion&#39;: &#39;NA&#39;, &#39;username&#39;: &#39;admin&#39;, &#39;password&#39;: &#39;Ixiaixiaixia!23&#39;}]
INFO:root:===== Authenticating all target chassis added on Controller Chassis 10.36.236.121
Polling for async operation ...
Completed async operation
INFO:root:===== Authentication complete for target chassis. Please check at https://10.36.236.121/chassislab/chassisui/settings/ixos-install
INFO:root:===== Sleeping for 30 secs to ensure all target chassis complete authentication =====
INFO:root:===== Updating Target Chassis =====
INFO:root:Upgrade started on 10.36.237.131
Polling for async operation ...
Completed async operation
22
Polling for async operation ...
<<<<<<< HEAD
Completed async operation
</code></pre>
