package com.timeweaver.apigateway.filters;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.UUID;

@Component
public class RequestLoggingFilter implements GlobalFilter, Ordered {
    private static final Logger log = LoggerFactory.getLogger(RequestLoggingFilter.class);
    public static final String REQ_ID_HEADER = "X-Request-Id";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, org.springframework.cloud.gateway.filter.GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String reqId = getOrCreateRequestId(request);

        long start = System.currentTimeMillis();
        ServerHttpRequest mutated = exchange.getRequest()
                .mutate()
                .headers(h -> h.add(REQ_ID_HEADER, reqId))
                .build();

        return chain.filter(exchange.mutate().request(mutated).build())
                .then(Mono.fromRunnable(() -> {
                    ServerHttpResponse response = exchange.getResponse();
                    long took = System.currentTimeMillis() - start;
                    response.getHeaders().add(REQ_ID_HEADER, reqId);
                    if (log.isInfoEnabled()) {
                        log.info("{} {} -> {} ({} ms) [{}]",
                                request.getMethod(), request.getURI().getPath(),
                                response.getStatusCode(), took, reqId);
                    }
                }));
    }

    private String getOrCreateRequestId(ServerHttpRequest request) {
        List<String> headers = request.getHeaders().get(REQ_ID_HEADER);
        if (headers != null && !headers.isEmpty()) {
            return headers.get(0);
        }
        return UUID.randomUUID().toString();
    }

    @Override
    public int getOrder() {
        return -1; // run early
    }
}
