import enum
from sqlalchemy import Column, Boolean, String, Integer, DateTime, Enum, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base

# Base class for ORM
Base = declarative_base()

# Enums
class Classifications(enum.Enum):
    TRI = 0
    PBT = 1
    Dioxin = 2

class Metal_Indicator(enum.Enum):
    Not_Metal = '0'
    Parent_Metals = '1'
    Listed_Metals = '2'
    Barium = '3'
    Qualified_Metals = '4'

# ORM models

class TriChemInfo(Base):
    __tablename__ = 'tri_chem_info'
    __table_args__ = (UniqueConstraint('tri_chem_id', 'srs_id'), )

    tri_chem_id = Column(String(15), primary_key=True)
    caac_ind = Column(Boolean)
    carc_ind = Column(Boolean)
    feds_ind = Column(Boolean)
    classification = Column(Enum(Classifications, name='classification'))
    metal_ind = Column(Enum(Metal_Indicator, name='metal_ind'))
    pbt_ind = Column(Boolean)
    pfas_ind = Column(Boolean)
    r3350_ind = Column(Boolean)
    srs_id = Column(String(20))
    unit_of_measure = Column(String(10))


class TriChemActivity(Base):
    __tablename__ = 'tri_chem_activity'
    __table_args__ = (UniqueConstraint('doc_ctrl_num'), )

    doc_ctrl_num = Column(String(13), primary_key=True)
    ancillary = Column(Boolean)
    article_component = Column(Boolean)
    byproduct = Column(Boolean)
    chem_processing_aid = Column(Boolean)
    formulation_component = Column(Boolean)
    imported = Column(Boolean)
    manufacture_aid = Column(Boolean)
    manufacture_impurity = Column(Boolean)
    process_impurity = Column(Boolean)
    produce = Column(Boolean)
    reactant = Column(Boolean)
    repackaging = Column(Boolean)
    sale_distribution = Column(Boolean)
    used_processed = Column(Boolean)


class TriFacilityHistory(Base):
    __tablename__ = 'tri_facility_history'
    __table_args__ = (PrimaryKeyConstraint('tri_facility_id', 'create_date'), )

    tri_facility_id = Column(String(15), primary_key=True)
    create_date = Column(DateTime, primary_key=True)
    parent_name = Column(String(100))
    name = Column(String(100), nullable=False)
    city = Column(String(50))
    county = Column(String(50))
    state = Column(String(50))
    epa_standardized_foreign_parent = Column(String(100))
    epa_standardized_parent = Column(String(100))
    primary_naics = Column(String(10))


class TriFormTotal(Base):
    __tablename__ = 'tri_form_total'
    __table_args__ = (UniqueConstraint('doc_ctrl_num'), )

    doc_ctrl_num = Column(String(13), primary_key=True)
    total_air_release = Column(String(50))
    total_land_release = Column(String(50))
    total_offsite_release = Column(String(50))
    total_onsite_release = Column(String(50))
    total_prod_waste = Column(String(50))
    total_recovery_transfer = Column(String(50))
    total_recycling_transfer = Column(String(50))
    total_water_release = Column(String(50))
    number_of_streams = Column(String(50))

class TRIFacilityDB(Base):
    __tablename__ = 'tri_facility_db'
    db_num = Column(String(15), primary_key=True)
    tri_facility_id = Column(String(15), primary_key=True)
    
class TRIFacilitynpdes(Base):
    # Permit a facility has to discharge chemical in specific bodies of water
    __tablename__ = 'tri_facility_npdes'

    asgn_npdes_ind = Column(Boolean)
    npdes_num = Column(String(10), primary_key=True)
    tri_facility_id = Column(String(15), primary_key=True)

class TRIFacilityRCRA(Base):
    #ID number given to facility that manages Regulated Hazardous Waste.
    __tablename__ = 'tri_facility_rcra'

    asgn_rcra_ind = Column(Boolean)
    rcra_num = Column(String(15), primary_key=True)
    tri_facility_id = Column(String(15), primary_key=True)

class TRIFacilityUIC(Base):
    # ID number for each Underground injection Well a facility has
    # Under the Safe Drinking Water Act
    
    __tablename__ = 'tri_facility_uic'
    
    asgn_uic_ind = Column(Boolean)
    uic_num = Column(String(10), primary_key=True)
    tri_facility_id = Column(String(15), primary_key=True)
    