from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.logging.qs_logger import get_qs_logger
from cloudshell.shell.core.context import ResourceCommandContext
import json


class AppLimitDeploymentError(Exception):
    pass


def _get_cp_restricted_attrs_dict(input_str):
    """
    sample input: 'poolA,3;poolB,4'
    output: {'poolA': 3, 'pool B', 4}
    :param str input_str:
    :return dict:
    """
    result = {}
    semicolon_split = input_str.split(";")
    for item in semicolon_split:
        comma_split = item.split(",")
        key = comma_split[0].strip()
        value = comma_split[1].strip()
        result[key] = value
    return result


def validate_app_deployment(context, request):
    """
    See sample json file for example of request
    :param ResourceCommandContext context:
    :param str request: json str of app deploy request
    :return:
    """
    # custom attribute attached to app resource models
    VM_RESOURCE_POOL_ATTR = "App Pool Name"

    # custom attribute attached to cloud provider resource, where pool limits will be defined
    CP_RESOURCE_RESTRICTED_ATTR = "Restricted App Model Pools"

    api = CloudShellSessionContext(context).get_api()
    res_id = context.reservation.reservation_id
    logger = get_qs_logger(log_group=res_id,
                           log_category=context.resource.model,
                           log_file_prefix=context.resource.name)

    # VALIDATE THAT CLOUD PROVIDER RESOURCE HAS POOL LIST Attribute
    cp_attrs = context.resource.attributes
    try:
        cp_pool_list_val = cp_attrs[CP_RESOURCE_RESTRICTED_ATTR]
    except KeyError:
        pass
    else:
        header_msg = "=== full request json ==="
        logger.debug(header_msg)
        logger.debug(request)

        # UNCOMMENT to print to sandbox console for debugging purposes
        # api.WriteMessageToReservationOutput(res_id, header_msg)
        # api.WriteMessageToReservationOutput(res_id, request)

        # UNPACK JSON OBJECT
        request_obj = json.loads(request)
        request_action_params = request_obj["driverRequest"]["actions"][0]["actionParams"]
        app_name = request_action_params["appName"]
        deployment = request_action_params["deployment"]
        app_resource = request_action_params["appResource"]
        app_resource_attrs = app_resource["attributes"]

        pool_attr_search = [attr for attr in app_resource_attrs if attr["attributeName"] == VM_RESOURCE_POOL_ATTR]
        if pool_attr_search:
            app_pool_attr_val = pool_attr_search[0]["attributeValue"]
            restricted_attrs_dict = _get_cp_restricted_attrs_dict(cp_pool_list_val)
            try:
                app_pool_limit = restricted_attrs_dict[app_pool_attr_val]
            except KeyError:
                not_found_msg = "{} pool name key not in cp restricted list {}".format(app_pool_attr_val,
                                                                                       restricted_attrs_dict)
                api.WriteMessageToReservationOutput(res_id, not_found_msg)
                logger.error(not_found_msg)
            else:
                # count deployed apps
                all_generic_app_resources = api.FindResources(resourceFamily="Generic App Family").Resources

                # collect matching apps
                matching_apps = []
                for resource in all_generic_app_resources:
                    attrs = api.GetResourceDetails(resource.Name).ResourceAttributes
                    attr_search = [attr for attr in attrs if attr.Name == VM_RESOURCE_POOL_ATTR]
                    if attr_search:
                        attr_val = attr_search[0].Value
                        if attr_val == app_pool_attr_val:
                            matching_apps.append(resource)

                # PERFORM VALIDATION
                if len(matching_apps) >= int(app_pool_limit):
                    matching_app_names = [r.Name for r in matching_apps]
                    exc_msg = "Can not deploy '{}'. The pool '{}' has reached it's limit of {}. Current Apps in Pool: {}".format(
                        app_name,
                        app_pool_attr_val,
                        app_pool_limit,
                        matching_app_names)
                    api.WriteMessageToReservationOutput(res_id, '<span style="color:red">{}</span>'.format(exc_msg))
                    logger.error(exc_msg)
                    raise AppLimitDeploymentError(exc_msg)

