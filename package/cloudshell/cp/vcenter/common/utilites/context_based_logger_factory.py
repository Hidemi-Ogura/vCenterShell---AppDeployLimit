from cloudshell.core.logger.qs_logger import get_qs_logger


class ContextBasedLoggerFactory(object):
    UNSUPPORTED_CONTEXT_PROVIDED = 'Unsuppported command context provided {0}'

    def create_logger_for_context(self, context):
        """
        Create QS Logger for command context AutoLoadCommandContext or ResourceCommandContext
        :param context:
        :return:
        """
        if self._is_instance_of(context, 'AutoLoadCommandContext'):
            reservation_id = 'Autoload'
            handler_name = 'Default'
        elif self._is_instance_of(context, 'ResourceCommandContext'):
            reservation_id = context.reservation.reservation_id
            handler_name = context.resource.name
        elif self._is_instance_of(context, 'ResourceRemoteCommandContext'):
            reservation_id = context.remote_reservation.reservation_id
            handler_name = context.resource.name
        else:
            raise Exception(ContextBasedLoggerFactory.UNSUPPORTED_CONTEXT_PROVIDED, context)
        logger = get_qs_logger(name='vCenterShell',
                               handler_name=handler_name,
                               reservation_id=reservation_id)
        return logger

    @staticmethod
    def _is_instance_of(context, type_name):
        return context.__class__.__name__ == type_name
