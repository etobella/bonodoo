from bonobo.nodes.io.base import Reader
from bonobo.config.configurables import Configurable
from bonobo.config import Option, Service, use_context
from xmlrpc import client as xmlrpclib
import ssl


class OdooServer:
    uid = False

    def __init__(
        self, hostname='localhost', database=False, port=8069,
        https=False, user=False, password=False
    ):
        super().__init__()
        self.database = database
        self.port = port
        self.https = https
        self.user = user
        self.password = password
        self.hostname = hostname

    @property
    def url(self):
        return '%s://%s:%s' % (
            'https' if self.https else 'http',
            self.hostname,
            self.port
        )

    @property
    def common(self):
        return xmlrpclib.ServerProxy(
            '{}/xmlrpc/2/common'.format(self.url),
            context=ssl._create_unverified_context(),
            allow_none=True
        )

    @property
    def models(self):
        return xmlrpclib.ServerProxy(
            '{}/xmlrpc/2/object'.format(self.url),
            context=ssl._create_unverified_context(),
            allow_none=True
        )

    def authenticate(self):
        self.uid = self.common.login(self.database, self.user, self.password)

    def execute(self, model, function, *args, **kwargs):
        if not self.uid:
            self.authenticate()
        return self.models.execute_kw(
            self.database, self.uid, self.password,
            model, function, args, kwargs
        )

    def write(self, model, ids, vals, *args, **kwargs):
        if isinstance(ids, int):
            ids = [ids]
        return self.execute(
            model,
            'write',
            *([ids, vals] + args),
            **kwargs
        )

    def read(self, model, ids, *args, **kwargs):
        if isinstance(ids, int):
            ids = [ids]
        return self.execute(
            model,
            'read',
            *([ids] + args),
            **kwargs
        )

    def search_read(self, model, *args, **kwargs):
        return self.execute(
            model,
            'search_read',
            *args,
            **kwargs
        )


class OdooBase(Configurable, Reader):
    config = Service('odoo.server')
    model = Option(
        type=str,
        required=True,
    )


@use_context
class OdooReader(OdooBase):
    domain = Option(
        type=list,
        default=[],
    )
    fields = Option(
        type=list,
        default=[],
    )
    limit = Option(
        type=int,
        required=False
    )

    def read(self, context, *args, config, **kwargs):
        new_args = [self.domain]
        new_args += args
        new_kwargs = kwargs.copy()
        if self.limit:
            new_kwargs['limit'] = self.limit
        if self.fields and not context.output_type:
            context.set_output_fields(self.fields)
        fields = context.get_output_fields()
        results = config.search_read(
            self.model,
            *new_args,
            **new_kwargs
        )
        if not fields:
            yield from results
        else:
            for result in results:
                final_result = []
                for field in fields:
                    final_result.append(result.get(field, False))
                yield tuple(final_result) if self.fields else result

    __call__ = read


@use_context
class OdooModelFunction(OdooBase):
    function = Option(
        type=str,
        required=True,
    )
    args = Option(type=list, default=[])
    kwargs = Option(type=dict, default={})

    def read(self, context, *values, config):
        result = config.execute(
            self.model,
            self.function,
            *self.args,
            **self.kwargs,
        )
        if isinstance(result, list):
            yield from result
        else:
            yield result

    __call__ = read
