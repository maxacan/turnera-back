from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)


# --- Dependencia DB ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
#   USUARIOS
# ==========================
@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = (
        db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    )
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    nuevo = models.Usuario(
        email=usuario.email,
        hashed_password=usuario.password,  # ⚠️ en producción encriptar con bcrypt
        rol=usuario.rol,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@app.get("/usuarios/", response_model=List[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()


@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
def detalle_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.put("/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
def actualizar_usuario(
    usuario_id: int, datos: schemas.UsuarioBase, db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.email = datos.email
    usuario.rol = datos.rol
    db.commit()
    db.refresh(usuario)
    return usuario


@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"ok": True, "mensaje": "Usuario eliminado"}


# ==========================
#   EMPRENDEDORES
# ==========================
@app.post("/emprendedores/", response_model=schemas.EmprendedorResponse)
def crear_emprendedor(
    emprendedor: schemas.EmprendedorCreate, db: Session = Depends(get_db)
):
    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.id == emprendedor.usuario_id)
        .first()
    )
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.rol != "emprendedor":
        raise HTTPException(status_code=400, detail="El usuario no es un emprendedor")

    nuevo = models.Emprendedor(**emprendedor.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@app.get("/emprendedores/", response_model=List[schemas.EmprendedorResponse])
def listar_emprendedores(db: Session = Depends(get_db)):
    return db.query(models.Emprendedor).all()


@app.get("/emprendedores/{emprendedor_id}", response_model=schemas.EmprendedorResponse)
def detalle_emprendedor(emprendedor_id: int, db: Session = Depends(get_db)):
    emprendedor = (
        db.query(models.Emprendedor)
        .filter(models.Emprendedor.id == emprendedor_id)
        .first()
    )
    if not emprendedor:
        raise HTTPException(status_code=404, detail="Emprendedor no encontrado")
    return emprendedor


@app.put("/emprendedores/{emprendedor_id}", response_model=schemas.EmprendedorResponse)
def actualizar_emprendedor(
    emprendedor_id: int, datos: schemas.EmprendedorBase, db: Session = Depends(get_db)
):
    emprendedor = (
        db.query(models.Emprendedor)
        .filter(models.Emprendedor.id == emprendedor_id)
        .first()
    )
    if not emprendedor:
        raise HTTPException(status_code=404, detail="Emprendedor no encontrado")
    for campo, valor in datos.dict().items():
        setattr(emprendedor, campo, valor)
    db.commit()
    db.refresh(emprendedor)
    return emprendedor


@app.delete("/emprendedores/{emprendedor_id}")
def eliminar_emprendedor(emprendedor_id: int, db: Session = Depends(get_db)):
    emprendedor = (
        db.query(models.Emprendedor)
        .filter(models.Emprendedor.id == emprendedor_id)
        .first()
    )
    if not emprendedor:
        raise HTTPException(status_code=404, detail="Emprendedor no encontrado")
    db.delete(emprendedor)
    db.commit()
    return {"ok": True, "mensaje": "Emprendedor eliminado"}


@app.get(
    "/emprendedores/{emprendedor_id}/servicios",
    response_model=list[schemas.ServicioResponse],
)
def listar_servicios_y_turnos(emprendedor_id: int, db: Session = Depends(get_db)):
    emprendedor = (
        db.query(models.Usuario)
        .filter(
            models.Usuario.id == emprendedor_id, models.Usuario.rol == "emprendedor"
        )
        .first()
    )
    if not emprendedor:
        raise HTTPException(status_code=404, detail="Emprendedor no encontrado")

    servicios = (
        db.query(models.Servicio)
        .filter(models.Servicio.emprendedor_id == emprendedor_id)
        .all()
    )
    return servicios


# ==========================
#   SERVICIOS
# ==========================
@app.post("/servicios/", response_model=schemas.ServicioResponseCreate)
def crear_servicio(servicio: schemas.ServicioCreate, db: Session = Depends(get_db)):
    emprendedor = (
        db.query(models.Emprendedor)
        .filter(models.Emprendedor.id == servicio.emprendedor_id)
        .first()
    )
    if not emprendedor:
        raise HTTPException(status_code=404, detail="Emprendedor no encontrado")

    nuevo = models.Servicio(**servicio.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@app.get("/servicios/", response_model=List[schemas.ServicioResponseCreate])
def listar_servicios(db: Session = Depends(get_db)):
    return db.query(models.Servicio).all()


@app.get("/servicios/{servicio_id}", response_model=schemas.ServicioResponseCreate)
def detalle_servicio(servicio_id: int, db: Session = Depends(get_db)):
    servicio = (
        db.query(models.Servicio).filter(models.Servicio.id == servicio_id).first()
    )
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio


@app.put("/servicios/{servicio_id}", response_model=schemas.ServicioResponseCreate)
def actualizar_servicio(
    servicio_id: int, datos: schemas.ServicioBase, db: Session = Depends(get_db)
):
    servicio = (
        db.query(models.Servicio).filter(models.Servicio.id == servicio_id).first()
    )
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    for campo, valor in datos.dict().items():
        setattr(servicio, campo, valor)
    db.commit()
    db.refresh(servicio)
    return servicio


@app.delete("/servicios/{servicio_id}")
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    servicio = (
        db.query(models.Servicio).filter(models.Servicio.id == servicio_id).first()
    )
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(servicio)
    db.commit()
    return {"ok": True, "mensaje": "Servicio eliminado"}


# ==========================
#   TURNOS
# ==========================
@app.post("/turnos/", response_model=schemas.TurnoResponseCreate)
def crear_turno(turno: schemas.TurnoCreate, db: Session = Depends(get_db)):
    servicio = (
        db.query(models.Servicio)
        .filter(models.Servicio.id == turno.servicio_id)
        .first()
    )
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    nuevo = models.Turno(**turno.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@app.get("/turnos/", response_model=List[schemas.TurnoResponseCreate])
def listar_turnos(db: Session = Depends(get_db)):
    return db.query(models.Turno).all()


@app.get("/turnos/{turno_id}", response_model=schemas.TurnoResponseCreate)
def detalle_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = db.query(models.Turno).filter(models.Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return turno


@app.put("/turnos/{turno_id}", response_model=schemas.TurnoResponseCreate)
def actualizar_turno(
    turno_id: int, datos: schemas.TurnoBase, db: Session = Depends(get_db)
):
    turno = db.query(models.Turno).filter(models.Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    for campo, valor in datos.dict().items():
        setattr(turno, campo, valor)
    db.commit()
    db.refresh(turno)
    return turno


@app.delete("/turnos/{turno_id}")
def eliminar_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = db.query(models.Turno).filter(models.Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    db.delete(turno)
    db.commit()
    return {"ok": True, "mensaje": "Turno eliminado"}


# ==========================
#   RESERVAS
# ==========================
@app.post("/reservas/", response_model=schemas.ReservaResponse)
def crear_reserva(reserva: schemas.ReservaCreate, db: Session = Depends(get_db)):
    turno = db.query(models.Turno).filter(models.Turno.id == reserva.turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    # Chequear capacidad
    reservas_existentes = (
        db.query(models.Reserva).filter(models.Reserva.turno_id == turno.id).count()
    )
    if reservas_existentes >= turno.capacidad:
        raise HTTPException(
            status_code=400, detail="No hay lugares disponibles en este turno"
        )

    # Chequear si el usuario ya reservó este turno
    ya_reservo = (
        db.query(models.Reserva)
        .filter(
            models.Reserva.turno_id == turno.id,
            models.Reserva.usuario_id == reserva.usuario_id,
        )
        .first()
    )
    if ya_reservo:
        raise HTTPException(status_code=400, detail="El usuario ya reservó este turno")

    nueva = models.Reserva(**reserva.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@app.get("/reservas/", response_model=List[schemas.ReservaResponse])
def listar_reservas(db: Session = Depends(get_db)):
    return db.query(models.Reserva).all()


@app.get("/reservas/{reserva_id}", response_model=schemas.ReservaResponse)
def detalle_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


@app.delete("/reservas/{reserva_id}")
def eliminar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    db.delete(reserva)
    db.commit()
    return {"ok": True, "mensaje": "Reserva eliminada"}
