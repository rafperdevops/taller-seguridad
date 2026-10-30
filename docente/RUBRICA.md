# 📊 Rúbrica de evaluación — Taller CampusShop

**Nota individual** aunque se trabaje en parejas. Cada integrante debe tener commits propios.

| Criterio | Excelente (100%) | Aceptable (60%) | Insuficiente (0–30%) | Peso |
|---|---|---|---|---|
| **Explotación** | Captura las 10 banderas con payload documentado | Captura 6–9 | Captura ≤5 | 30% |
| **Mitigación** | 16 pruebas en verde y el código aplica la defensa correcta (no un parche que solo engaña al test) | 10–15 pruebas en verde | <10 en verde | 40% |
| **Informe** | Causa raíz clara, relación con la diapositiva, antes/después | Describe el fix sin causa raíz | Incompleto o copiado | 20% |
| **Intercambio entre parejas** | Encuentra un bypass real o defiende sin bypass | Participa parcialmente | No participa | 10% |

## Penalizaciones
- Parche que modifica la prueba en vez del código vulnerable: **mitigación = 0**.
- Sin commits individuales: ese integrante se evalúa solo por lo que evidencie.
- Mensajes de commit no descriptivos (`fix`, `update`, `asdf`): −10% del criterio mitigación.

## Verificación rápida del profesor
```bash
# Sobre la entrega del alumno:
pytest -v                      # deben pasar las 16
grep -rn "shell=True\|innerHTML\|md5\|UNION\|allow_origins=\[\"\*\"\]" campusshop/   # no debe quedar nada
```

## Checklist por vulnerabilidad corregida
- [ ] 01 SQLi: consultas parametrizadas en login y buscador
- [ ] 02 XSS: sin `|safe`, `textContent`, CSP, cookie HttpOnly
- [ ] 03 Comandos: sin `shell=True`, argumentos en lista, host validado
- [ ] 04 IDOR: autorización por dueño en facturas
- [ ] 05 Idempotencia: `UNIQUE` + manejo de IntegrityError
- [ ] 06 CSRF: token en formulario + cookie SameSite
- [ ] 07 Auth: hash con sal, sin MD5
- [ ] 08 SSRF: lista blanca + bloqueo de IP internas
- [ ] 09 Path traversal: ruta resuelta y validada
- [ ] 10 Config: debug off, CORS acotado, secreto fuera del código, cabeceras
