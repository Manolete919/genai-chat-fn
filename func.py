import io
import json
import logging
import oci
from fdk import response


# 🔥 Modelo que ya tienes en tu OCI (Gemini Flash)
MODEL_ID = "ocid1.generativeaimodel.oc1.iad.amaaaaaask7dceyaeo4ehrn25guuats5s45hnvswlhxo6riop275l2bkr2vq"


def handler(ctx, data: io.BytesIO = None):
    try:

        # --------------------------------------------------
        # 1. Validación de entrada
        # --------------------------------------------------
        if data is None or not data.getvalue():
            return response.Response(
                ctx,
                response_data=json.dumps({"error": "Empty request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )

        body = json.loads(data.getvalue())
        prompt = body.get("message")

        if not prompt:
            return response.Response(
                ctx,
                response_data=json.dumps({"error": "Field 'message' is required"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )

        # --------------------------------------------------
        # 2. Auth (Resource Principal)
        # --------------------------------------------------
        signer = oci.auth.signers.get_resource_principals_signer()

        client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config={},
            signer=signer,
            service_endpoint="https://inference.generativeai.us-ashburn-1.oci.oraclecloud.com"
        )

        # --------------------------------------------------
        # 3. Request de chat
        # --------------------------------------------------
        chat_request = oci.generative_ai_inference.models.GenericChatRequest(
            messages=[
                oci.generative_ai_inference.models.UserMessage(
                    content=[
                        oci.generative_ai_inference.models.TextContent(text=prompt)
                    ]
                )
            ],
            max_tokens=600,
            temperature=0.7,
            top_p=0.9
        )

        # --------------------------------------------------
        # 4. ChatDetails (CORRECTO)
        # --------------------------------------------------
        chat_details = oci.generative_ai_inference.models.ChatDetails(
            compartment_id="ocid1.compartment.oc1..aaaaaaaacsfl743vdv7ufqbqk2r3ujjejdvumuigczw3gx45owyghvnam6zq",
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=MODEL_ID
            ),
            chat_request=chat_request
        )

        # --------------------------------------------------
        # 5. Llamada al modelo
        # --------------------------------------------------
        client_response = client.chat(chat_details=chat_details)

        output_text = client_response.data.chat_response.choices[0].message.content[0].text

        # --------------------------------------------------
        # 6. Respuesta final
        # --------------------------------------------------
        return response.Response(
            ctx,
            response_data=json.dumps({"output": output_text}),
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        logging.getLogger().exception("Function error")
        return response.Response(
            ctx,
            response_data=json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )