package com.ecs.common.security;

import com.ecs.common.core.exception.DomainException;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

import org.springframework.context.annotation.EnableAspectJAutoProxy;

@Aspect
@Component
@EnableAspectJAutoProxy
public class RoleGuardAspect {

    @Before("@annotation(requireRole)")
    public void check(JoinPoint joinPoint, RequireRole requireRole) {
        GatewayPrincipal principal = GatewayHeaders.current();
        for (String role : requireRole.value()) {
            if (principal.hasRole(role) || principal.hasRole("SUPER_ADMIN")) {
                return;
            }
        }
        throw new DomainException(HttpStatus.FORBIDDEN, "FORBIDDEN", "Insufficient role for " + joinPoint.getSignature());
    }
}
