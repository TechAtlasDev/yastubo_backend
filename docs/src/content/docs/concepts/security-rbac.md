---
title: Seguridad y RBAC
description: Cómo protegemos los datos y gestionamos roles en Yastubo.
---

La seguridad en Yastubo se basa en la protección de los datos sensibles de los migrantes y sus familias. Hemos implementado un sistema robusto de **Control de Acceso Basado en Roles (RBAC)** y una estructura de **Multi-tenancy** (Workspaces) para asegurar la privacidad de la información.

## Core Benefits

*   **Aislamiento de Datos:** Cada usuario opera dentro de uno o más "Workspaces", garantizando que la información de un reseller no sea visible para otro.
*   **Granularidad de Permisos:** Los endpoints de la API están protegidos por roles específicos que definen qué acciones puede realizar cada usuario.
*   **Autenticación Stateless:** Utilizamos JWT (JSON Web Tokens) para una autenticación rápida y segura, permitiendo el escalamiento horizontal.

## Deep Dive Técnico: Gestión de Roles y Permisos

El sistema utiliza un decorador `require_role` para inyectar lógica de autorización directamente en los endpoints de FastAPI.

### Roles Predefinidos
1.  **SUPER_ADMIN:** Acceso total a todos los módulos y configuraciones del sistema.
2.  **ADMIN:** Gestión de pólizas, beneficiarios y pagos dentro de su workspace.
3.  **OPERATOR:** Gestión operativa básica (ej. soporte a siniestros).
4.  **RESELLER:** Solo acceso a sus propios leads y pólizas emitidas.

### Inyección de Dependencias para RBAC

```python
# app/modules/auth/dependencies.py

def require_role(*roles: str) -> Callable:
    def role_checker(user: User = Depends(get_current_user)):
        user_roles = [role.name for role in user.roles]
        # Verificamos si el usuario posee al menos uno de los roles requeridos
        if not any(role in user_roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para realizar esta acción"
            )
        return user
    return role_checker
```
*Este enfoque asegura que el código de negocio no tenga que preocuparse por la lógica de autorización, ya que es gestionada por la capa de dependencias de la API.*

## Multi-tenancy con Workspaces

El sistema permite que un usuario pertenezca a múltiples entornos de trabajo. Para gestionar esto, el backend espera un header `X-Workspace-Id` en las peticiones que requieren contexto de empresa.

### Resolución de Workspace
Si un usuario pertenece a un solo workspace, el sistema lo selecciona automáticamente. Si pertenece a varios, debe especificarlo en el header:

```python
# app/modules/auth/dependencies.py

async def get_current_workspace_id(
    user: User = Depends(get_current_user),
    workspace_id: Optional[uuid.UUID] = Header(None, alias="X-Workspace-Id"),
) -> uuid.UUID:
    # Lógica de validación de pertenencia al workspace...
```
*Esto previene accesos accidentales o malintencionados a datos de otros clientes u organizaciones.*

## Flujo de Autenticación y Autorización

![Security & RBAC Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844195/49243f09-61aa-4dac-9fcb-41bd7536ee75.png)
