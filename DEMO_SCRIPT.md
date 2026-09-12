# Amnesia — demo de concurso (2 minutos)

1. Muestra el grupo de Telegram con Amnesia como administrador. Explica: “Amnesia escucha este grupo, conserva decisiones y solo habla ante una señal importante.”
2. Envía: `Queda acordado que todos los FortiGate de producción deben quedar en 7.4.11.` El bot responde: **🧠 Amnesia remembered a decision**.
3. Ejecuta `/decisions` para visualizar la memoria activa.
4. Envía: `Dejemos el FortiGate de Bajío en 7.4.9.` La tarjeta indica la decisión anterior, la nueva propuesta y 95% de confianza.
5. Pulsa **Create exception**: la decisión global permanece activa y queda trazada una excepción aprobada. Alternativamente, usa **Update decision** para mostrar que la anterior pasa a `superseded` y nace una nueva decisión activa.
6. Ejecuta `/conflicts`. Cierra explicando que no hay webhook, servidores ni infraestructura adicional: solo polling, OpenAI Agents SDK, SQLite y revisión humana.

Como respaldo, ejecuta `python demo_local.py`: reproduce decisión y contradicción sin Telegram, internet ni API key.
