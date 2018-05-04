#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <string.h>

/*
 * Somewhat risky business
 *   Call "chpasswd" without prompting for original password.
 *   Probably OK on the embedded system this is targetted for...
 *   He says, in denial.
 */

int
main(int argc, char **argv)
{
	char *user;
	struct passwd *p;
	FILE *fp;
	char pass[64];
	
	
	if (argc < 1)
	{
		exit (0);
	}
	memset(pass, (char)0, sizeof(pass));
	strncpy (pass, argv[1], 63);
	if (strlen(pass) < 1)
	{
		exit (0);
	}
	
	/*
	 * Base username strictly on uid of running process
	 */
	p = getpwuid(getuid());
	user = p->pw_name;
	
	/*
	 * Switch to root--if this doesn't work, the chpass will just fail
	 *   and no harm.
	 */
	setuid(0);
	fp = popen ("chpasswd", "w");
	fprintf (fp, "%s:%s\n", user, pass);
	pclose(fp);
	exit(0);
	
}
