#include "../include/scanner.h"

void scanner(void) {
    FILE *f;
    char * buf;

    f=popen("lsusb", "r");
    if (f==NULL) {
        perror("1 - Error");
        return errno;
    }

    buf=malloc(BUF_SIZE);
    if (buf==NULL) {
        perror("2 - Error");
        pclose(f);
        return errno;
    }

    while(fgets(buf,BUF_SIZE,f)!=NULL) {
        printf("%s",buf);
    }
    puts("");

    pclose(f);
    free(buf);

}