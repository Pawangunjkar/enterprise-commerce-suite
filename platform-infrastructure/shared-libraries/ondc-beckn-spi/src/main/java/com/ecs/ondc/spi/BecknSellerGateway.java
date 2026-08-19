package com.ecs.ondc.spi;

public interface BecknSellerGateway {
    BecknResponse search(BecknRequest request);
    BecknResponse select(BecknRequest request);
    BecknResponse init(BecknRequest request);
    BecknResponse confirm(BecknRequest request);
    BecknResponse status(BecknRequest request);
    BecknResponse track(BecknRequest request);
    BecknResponse cancel(BecknRequest request);
}
