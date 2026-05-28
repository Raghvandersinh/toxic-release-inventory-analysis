import enum
from sqlalchemy import Column, Boolean, String, Integer, DateTime, Enum, UniqueConstraint, PrimaryKeyConstraint, ForeignKey, Text
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
class TRIReportingForm(Base):
    __tablename__ = 'tri_reporting_form'
    doc_ctrl_num =  Column(String(13), primary_key=True)
    tri_facility_id = Column(String(15), nullable=False, index=True)
    tri_chem_id = Column(String(15), ForeignKey('tri_chem_info.tri_chem_id'), index=True)
    reporting_year = Column(Integer)
    
class TriChemInfo(Base):
    __tablename__ = 'tri_chem_info'
    tri_chem_id = Column(String(15), primary_key=True)
    chem_name = Column(String(750))
    caac_ind = Column(Boolean)
    carc_ind = Column(Boolean)
    feds_ind = Column(Boolean)
    classification = Column(Enum(Classifications, name='classification'))
    metal_ind = Column(Enum(Metal_Indicator, name='metal_ind'))
    pbt_ind = Column(Boolean)
    pfas_ind = Column(Boolean)
    r3350_ind = Column(Boolean)
    srs_id = Column(String(20))
    unit_of_measure = Column(String(11))


class TriChemActivity(Base):
    __tablename__ = 'tri_chem_activity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_ctrl_num = Column(String(13), ForeignKey('tri_reporting_form.doc_ctrl_num'), index=True)
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    tri_facility_id = Column(String(15), nullable=False, index=True)
    create_date = Column(DateTime, nullable=False)
    parent_name = Column(String(100))
    name = Column(String(100), nullable=False)
    city = Column(String(50))
    county = Column(String(50))
    state = Column(String(50))
    epa_standardized_foreign_parent = Column(String(100))
    epa_standardized_parent = Column(String(100))
    primary_naics = Column(String(10))
    reporting_year = Column(Integer)

class TriFormTotal(Base):
    __tablename__ = 'tri_form_total'

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_ctrl_num = Column(String(13), ForeignKey('tri_reporting_form.doc_ctrl_num'), index=True)
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
    tri_facility_id = Column(String(15), nullable=False, index=True)
    
class TRIFacilitynpdes(Base):
    # Permit a facility has to discharge chemical in specific bodies of water
    __tablename__ = 'tri_facility_npdes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asgn_npdes_ind = Column(Boolean)
    npdes_num = Column(String(15))
    tri_facility_id = Column(String(15), nullable=False, index=True)

class TRIFacilityRCRA(Base):
    #ID number given to facility that manages Regulated Hazardous Waste.
    __tablename__ = 'tri_facility_rcra'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asgn_rcra_ind = Column(Boolean)
    rcra_num = Column(String(20))
    tri_facility_id = Column(String(15), nullable=False, index=True)

class TRIFacilityUIC(Base):
    # ID number for each Underground injection Well a facility has
    # Under the Safe Drinking Water Act
    
    __tablename__ = 'tri_facility_uic'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    asgn_uic_ind = Column(Boolean)
    uic_num = Column(String(20))
    tri_facility_id = Column(String(15), nullable=False, index=True)

class TRISubmissionNAICS(Base):
    __tablename__ = 'tri_submission_naics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tri_facility_id = Column(String(15), nullable=False, index=True)
    doc_ctrl_num = Column(String(13), ForeignKey('tri_reporting_form.doc_ctrl_num'), index=True)
    naics_code = Column(String(6))
    industry_code = Column(String(6))
    source = Column(String(10))
    
class NAICSCodes(Base):
    __tablename__ = 'naics_code'
    naics_code = Column(String(10), primary_key=True)
    name = Column(String)
    type = Column(String)
    