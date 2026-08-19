package com.ecs.payment.spi;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.client.j2se.MatrixToImageWriter;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;

import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.UUID;

public final class BharatQrFactory {

    private BharatQrFactory() {}

    public static DynamicBharatQr create(String vpa, String merchantName, String mcc, String orderId, BigDecimal amount) {
        String txnId = UUID.randomUUID().toString().replace("-", "").substring(0, 20);
        String uri = "upi://pay?pa=" + enc(vpa)
                + "&pn=" + enc(merchantName)
                + "&mc=" + enc(mcc)
                + "&tid=" + enc(txnId)
                + "&tr=" + enc(orderId)
                + "&am=" + amount.toPlainString()
                + "&cu=INR";
        return new DynamicBharatQr(uri, toPngBase64(uri), txnId, vpa);
    }

    public static UpiIntentResponse intents(String upiUri) {
        String encoded = enc(upiUri);
        return new UpiIntentResponse(
                "tez://upi/pay?data=" + encoded,
                "phonepe://pay?pa=" + encoded,
                "paytmmp://pay?pa=" + encoded,
                "credpay://upi?uri=" + encoded,
                upiUri
        );
    }

    private static String enc(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }

    private static String toPngBase64(String content) {
        try {
            BitMatrix matrix = new QRCodeWriter().encode(content, BarcodeFormat.QR_CODE, 320, 320);
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            MatrixToImageWriter.writeToStream(matrix, "PNG", out);
            return Base64.getEncoder().encodeToString(out.toByteArray());
        } catch (Exception ex) {
            throw new IllegalStateException("Unable to render BharatQR", ex);
        }
    }
}
