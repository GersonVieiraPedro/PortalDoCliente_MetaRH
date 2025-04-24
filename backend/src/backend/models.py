from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Mapped, registry, mapped_column



TabelaRegistro = registry()

@TabelaRegistro.mapped_as_dataclass
class TB_Usuarios:
    __tablename__  ='TB_Usuarios'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    Nome: Mapped[str]
    Email: Mapped[str] = mapped_column(unique=True)
    Senha: Mapped[str]
    CNPJ: Mapped[str]
    TipoAcesso: Mapped[str] = mapped_column(init=False, server_default=text('Cliente'))
    Acesso: Mapped[str] = mapped_column(init=False, server_default=None)
    PipedriveID: Mapped[str] = mapped_column(init=False, server_default=text('NãoMapeado'))
    CodigoCliente: Mapped[str] = mapped_column(init=False, server_default=text('NãoMapeado'))
    Status: Mapped[bool] = mapped_column(default=False, server_default=text("FALSE"))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))



