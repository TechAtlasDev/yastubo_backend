---
title: Auth (Identidad y Acceso)
description: Gestión de usuarios, sesiones JWT y Control de Acceso Basado en Roles (RBAC).
---

El módulo de **Auth** es el guardián de la seguridad en Yastubo. No solo gestiona quién puede entrar al sistema, sino qué acciones puede realizar según su rol y pertenencia a un espacio de trabajo (Workspace).

## Key Features

*   **Durable Sessions**: Implementación de tokens de acceso (JWT) y de refresco (Redis) para sesiones seguras y persistentes.
*   **Audit-First Design**: Cada registro y asignación de rol se audita automáticamente mediante decoradores de sistema.
*   **RBAC Nativo**: Soporte para roles como `ADMIN`, `VENDEDOR` y `CLIENTE` desde el núcleo.
*   **Cifrado Robusto**: Uso de algoritmos de hash modernos para la protección de credenciales.

:::tip[Seguridad]
Los tokens de acceso son de vida corta (30 min), mientras que los tokens de refresco se almacenan en Redis con un tiempo de expiración configurable, permitiendo la revocación inmediata de sesiones si es necesario.
:::

## Deep Dive Técnico

### Flujo de Autenticación
El sistema utiliza una arquitectura de doble token:
1.  **Access Token (JWT)**: Contiene los `roles` y el `user_id`. Se envía en el header `Authorization: Bearer`.
2.  **Refresh Token**: Un identificador único almacenado en **Redis** vinculado al usuario. Se utiliza exclusivamente para obtener un nuevo par de tokens sin requerir las credenciales nuevamente.

### Lógica de Registro
Al registrar un nuevo usuario, el sistema:
*   Verifica la unicidad del email.
*   Genera un hash de la contraseña usando `bcrypt` (o similar).
*   Asigna automáticamente el rol `CLIENTE`.
*   Crea una entrada en el log de auditoría (`USER_REGISTERED`).

### Gestión de Roles (RBAC)
Los roles no son simples strings; están vinculados a capacidades dentro del sistema. La asignación de roles requiere privilegios de `ADMIN` y se rastrea quién realizó la asignación.

## Ejemplo Práctico

A continuación, un ejemplo de cómo se implementa el registro de un usuario en el servicio de backend:

```python
@audited(action="USER_REGISTERED", entity="User")
async def register_user(db: AsyncSession, data: UserRegister) -> User:
    """
    Registra un nuevo usuario y le asigna el rol CLIENTE por defecto.
    """
    # 1. Verificar si el correo ya existe para evitar duplicados
    existing_user = await get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="El correo ya está registrado"
        )

    # 2. Cifrar la contraseña antes de guardarla
    hashed_password = get_password_hash(data.password)
    user = User(
        email=data.email,
        hashed_password=hashed_password,
        full_name=data.full_name,
        phone=data.phone,
        is_active=True, # El usuario se activa inmediatamente
    )
    db.add(user)
    await db.flush()  # Obtenemos el ID generado

    # 3. Asignación automática de rol inicial
    role_result = await db.execute(select(Role).where(Role.name == "CLIENTE"))
    cliente_role = role_result.scalar_one_or_none()
    if cliente_role:
        user_role = UserRole(user_id=user.id, role_id=cliente_role.id)
        db.add(user_role)

    await db.commit()
    await db.refresh(user, ["roles"])
    return user
```

## Diagrama de Proceso

![Auth Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844673/2e98efda-847e-49fc-be8e-5ab03463676a.png)

## Endpoints Principales

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Registro de nuevos usuarios. |
| `POST` | `/api/v1/auth/login` | Intercambio de credenciales por tokens. |
| `POST` | `/api/v1/auth/refresh` | Renovación de sesión usando Refresh Token. |
| `GET` | `/api/v1/auth/me` | Obtención del perfil del usuario actual. |
