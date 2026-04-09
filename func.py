import io
import json
import logging
import oci
from fdk import response


def handler(ctx, data: io.BytesIO = None):
    try:
        # --------------------------------------------------
        # 1. Leer payload de entrada
        # --------------------------------------------------
        body = json.loads(data.getvalue())
        prompt = body.get("message")

        if not prompt:
            return response.Response(
                ctx,
                response_data=json.dumps(
                    {"error": "Field 'message' is required"}
                ),
                status=400,
                headers={"Content-Type": "application/json"}
            )

        # --------------------------------------------------
        # 2. Autenticación: Resource Principal (OCI Functions)
        # --------------------------------------------------
        signer = oci.auth.signers.get_resource_principals_signer()

        client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config={},
            signer=signer,
            service_endpoint="https://inference.generativeai.us-ashburn-1.oci.oraclecloud.com"
        )

        # --------------------------------------------------
        # 3. Construcción del request de chat (Generic)
        # --------------------------------------------------
        chat_request = oci.generative_ai_inference.models.GenericChatRequest(
            messages=[
                oci.generative_ai_inference.models.UserMessage(
                    content=[
                        oci.generative_ai_inference.models.TextContent(
                            text=prompt
                        )
                    ]
                )
            ],
            max_tokens=600,
            temperature=1.0,
            top_p=0.75
        )

        chat_details = oci.generative_ai_inference.models.ChatDetails(
            compartment_id="ocid1.compartment.oc1..aaaaaaaacsfl743vdv7ufqbqk2r3ujjejdvumuigczw3gx45owyghvnam6zq",
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                # ✅ Modelo on-demand oficial (mismo del ejemplo Java/Python)
                model_id="ocid1.generativeaimodel.oc1.iad.amaaaaaask7dceyah6tjdejjashngznsylutuhhvufukzb2g2ls54g2flsfq"
            ),
            chat_request=chat_request
        )

        # --------------------------------------------------
        # 4. Invocación al modelo
        # --------------------------------------------------
        chat_response = client.chat(
            oci.generative_ai_inference.models.ChatRequest(
                chat_details=chat_details
            )
        )

        output_text = (
            chat_response.data.chat_response
            .choices[0]
            .message.content[0].text
        )

        # --------------------------------------------------
        # 5. Respuesta limpia
        # --------------------------------------------------
        return response.Response(
            ctx,
            response_data=json.dumps({"output": output_text}),
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        logging.getLogger().error(str(e))
        return response.Response(
            ctx,
            response_data=json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"}
        )