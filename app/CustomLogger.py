from gunicorn.glogging import Logger
import json
import traceback

access_format = {
    "time": "t",
    "remote": "[{x-forwarded-for}i]",
    "method": "m",
    "status": "s",
    "resource": "U",
    "query": "q",
    "hostname": "{Host}i"
}


class CustomLogger(Logger):
    def access(self, resp, req, environ, request_time):
        if not (self.cfg.accesslog or self.cfg.logconfig or
                self.cfg.logconfig_dict or
                (self.cfg.syslog and not self.cfg.disable_redirect_access_to_syslog)):
            return
        safe_atoms = self.atoms_wrapper_class(self.atoms(resp, req, environ,
                                                         request_time))

        log_object = {k: safe_atoms[access_format[k]] for k in access_format.keys()}
        try:
            self.access_log.info(json.dumps(log_object))
        except:
            self.error(traceback.format_exc())
