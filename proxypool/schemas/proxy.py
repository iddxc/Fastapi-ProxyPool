from pydantic import BaseModel


class Proxy(BaseModel):
    host: str
    port: int

    def is_valid_proxy(self):
        """
        check this proxy is valid
        """
        return self.is_ip_valid()

    def is_ip_valid(self):
        """
        check this string is within ip format
        """
        a = self.host.split(".")
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    @classmethod
    def convert_proxy_or_proxies(cls, data):
        """
        convert list of str to valid proxies or proxy
        :param data:
        :return:
        """
        if not data:
            return None
        # if list of proxies
        if isinstance(data, list):
            result = []
            for item in data:
                host, port = item.strip().split(':')
                proxy = Proxy(host=host, port=int(port))
                # skip invalid item
                if not proxy.is_valid_proxy(): continue
                result.append(proxy)
            return result
        if isinstance(data, str):
            host, port = data.split(':')
            proxy = Proxy(host=host, port=int(port))
            return proxy if proxy.is_valid_proxy() else None

    def __str__(self):
        return f"{self.host}:{self.port}"

    def string(self):
        return self.__str__()
