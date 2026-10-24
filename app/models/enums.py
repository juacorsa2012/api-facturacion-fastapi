import enum

class Estado(str, enum.Enum):
  ALTA = "ALTA"
  BAJA = "BAJA"

class Empresa(str, enum.Enum):
  GTRES = "GTRES"
  LEMS = "LEMS"

class FormaPago(str, enum.Enum):
  NINGUNO = "NINGUNO"
  RECIBO = "RECIBO"
  TRANSFERENCIA = "TRANSFERENCIA"

class Vencimiento(str, enum.Enum):
  UN_MES = "UN_MES"
  DOS_MESES = "DOS_MESES"
  QUINCE_DIAS = "QUINCE_DIAS"
  VEINTE_DIAS = "VEINTE_DIAS"

class Ciclo(str, enum.Enum):
  ANUAL = "ANUAL"
  SEMESTRAL = "SEMESTRAL"
  TRIMESTRAL = "TRIMESTRAL"
  BIMENSUAL = "BIMENSUAL"
  MENSUAL = "MENSUAL"