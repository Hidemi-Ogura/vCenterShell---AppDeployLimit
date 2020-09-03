from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow
from cloudshell.workflow.orchestration.sandbox import Sandbox, WorkFlowException
from first_module import first_module_flow
from AppDeploymentException import AppLimitDeploymentError
import time

sandbox = Sandbox()
sandbox.suppress_exceptions = False
api = sandbox.automation_api
res_id = sandbox.id

DefaultSetupWorkflow().register(sandbox)
# sandbox.workflow.on_preparation_ended(first_module_flow, None)

try:
    sandbox.execute_setup()
except WorkFlowException as e:
    if "AppLimitDeploymentError" in str(e):
        err_msg = "App Limit Deployment Error thrown during setup: {}".format(str(e))
        api.WriteMessageToReservationOutput(res_id, err_msg)
        api.SetReservationLiveStatus(reservationId=res_id, liveStatusName="Error", additionalInfo=err_msg)
        api.WriteMessageToReservationOutput(res_id, "=== ENDING RESERVATION ===")
        time.sleep(3)
        api.EndReservation(res_id)
    else:
        err_msg = "Error thrown during setup: {}".format(str(e))
        raise
